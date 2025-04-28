import asyncio
import os
from dataclasses import dataclass

import asyncpg
from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext


class PostgresConn:
    """PostgreSQL database connection for banking application."""
    
    def __init__(self, connection_string=None):
        self.pool = None
        self.connection_string = connection_string or self._get_default_connection_string()
        
    def _get_default_connection_string(self):
        """Get connection details from environment variables or use defaults."""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        database = os.getenv("DB_NAME", "bankdb")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
    async def connect(self):
        """Connect to the database."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.connection_string)
            print("Connected to database pool")
        
    async def close(self):
        """Close database connection."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("Database connection pool closed")
            
    async def customer_name(self, *, id: int) -> str | None:
        """Get customer name from database."""
        if not self.pool:
            await self.connect()
            
        async with self.pool.acquire() as conn:
            query = "SELECT name FROM customers WHERE id = $1"
            result = await conn.fetchval(query, id)
            return result
    
    async def customer_balance(self, *, id: int, include_pending: bool) -> float:
        """Get customer's total balance from database."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            print(f"Checking balance for customer ID {id}")
            
            # Get all customer accounts
            accounts_query = "SELECT id FROM accounts WHERE customer_id = $1"
            account_ids = await conn.fetch(accounts_query, id)
            
            if not account_ids:
                raise ValueError('Customer not found or has no accounts')
            
            total_balance = 0.0
            
            # Process all customer accounts
            for record in account_ids:
                account_id = record['id']
                
                # Get base account balance
                balance_query = "SELECT balance FROM accounts WHERE id = $1"
                base_balance = await conn.fetchval(balance_query, account_id)
                
                # Convert Decimal to float
                if base_balance is not None:
                    base_balance = float(base_balance)
                else:
                    base_balance = 0.0
                
                # Add transactions based on status
                if include_pending:
                    # Include both confirmed and pending transactions
                    transactions_query = """
                        SELECT COALESCE(SUM(amount), 0.0) FROM transactions 
                        WHERE account_id = $1 AND status IN ('confirmed', 'pending')
                    """
                else:
                    # Only confirmed transactions
                    transactions_query = """
                        SELECT COALESCE(SUM(amount), 0.0) FROM transactions 
                        WHERE account_id = $1 AND status = 'confirmed'
                    """
                    
                transactions_sum = await conn.fetchval(transactions_query, account_id)
                
                # Convert Decimal to float
                if transactions_sum is not None:
                    transactions_sum = float(transactions_sum)
                else:
                    transactions_sum = 0.0
                
                # Add to total balance
                total_balance += base_balance + transactions_sum
                
            return total_balance
    
    async def block_card(self, *, customer_id: int) -> bool:
        """Block customer's cards."""
        if not self.pool:
            await self.connect()
            
        async with self.pool.acquire() as conn:
            print(f"Blocking cards for customer ID {customer_id}")
            
            # First find all account IDs for this customer
            account_query = "SELECT id FROM accounts WHERE customer_id = $1"
            account_ids = await conn.fetch(account_query, customer_id)
            
            if not account_ids:
                return False
                
            # Block all cards linked to these accounts
            account_id_list = [record['id'] for record in account_ids]
            
            # Use ANY operator to update cards for multiple accounts
            update_query = """
                UPDATE cards 
                SET status = 'blocked' 
                WHERE account_id = ANY($1::int[]) 
                AND status = 'active'
            """
            
            result = await conn.execute(update_query, account_id_list)
            
            # Returns True if at least one card was blocked
            return "UPDATE" in result


@dataclass
class SupportDependencies:
    customer_id: int
    db: PostgresConn


class SupportResult(BaseModel):
    support_advice: str = Field(description='Advice provided to the customer')
    block_card: bool = Field(description='Whether to block their card or not')
    risk: int = Field(description='Risk level of query', ge=0, le=10)


support_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDependencies,
    result_type=SupportResult,
    system_prompt=(
        'You are a bank customer support agent. Provide support to the customer '
        'and assess the risk level of their query. Use the customer\'s name in your response.'
    ),
)


@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    """Add customer name to system prompt."""
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"The customer's name is {customer_name!r}"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> str:
    print(f"Checking balance for customer ID {ctx.deps.customer_id}")
    """Returns the customer's current account balance."""
    try:
        balance = await ctx.deps.db.customer_balance(
            id=ctx.deps.customer_id,
            include_pending=include_pending,
        )
        return f'${balance:.2f}'
    except ValueError as e:
        return f"Error: {str(e)}"


@support_agent.tool
async def block_customer_cards(ctx: RunContext[SupportDependencies]) -> str:
    """Blocks all cards for the customer."""
    print(f"Blocking cards for customer ID {ctx.deps.customer_id}")
    try:
        result = await ctx.deps.db.block_card(customer_id=ctx.deps.customer_id)
        if result:
            return "Cards have been successfully blocked. A new card will be sent to the customer."
        else:
            return "No active cards to block."
    except Exception as e:
        return f"Error blocking cards: {str(e)}"


async def main():
    # Create database connection
    db = PostgresConn()
    
    try:
        # Connect to database
        await db.connect()
        
        # Create dependencies
        deps = SupportDependencies(customer_id=123, db=db)
        
        # Run agent
        print("\n=== Query 1: Balance Inquiry ===")
        result = await support_agent.run('How much money do I have?', deps=deps)
        print(result.data)
        
        print("\n=== Query 2: Lost Card ===")
        result = await support_agent.run('I lost my card!', deps=deps)
        print(result.data)
        
    finally:
        # Close database connection
        await db.close()


if __name__ == '__main__':
    asyncio.run(main())