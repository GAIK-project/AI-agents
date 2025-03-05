# Pydantic-AI Bank Support Agent Demo

This demo showcases a bank support agent built with Pydantic-AI that retrieves customer data from a PostgreSQL database.

## Features

- **Real PostgreSQL Database**: Runs in Docker for easy setup
- **pgAdmin Interface**: Web-based database management
- **Pydantic-AI Agent**: AI-powered bank support agent
- **Dependency Injection**: Demonstrates how to connect external data sources
- **Function Tools**: Shows practical use of tools to query data

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ with Poetry or pip

### Step 1: Set Up the Database

1. Clone this repository or download the files:

   - `docker-compose.yml`
   - `init-db.sql`
   - `main.py`

2. Launch PostgreSQL and pgAdmin containers:

   ```bash
   docker-compose up -d
   ```

3. Verify containers are running:
   ```bash
   docker-compose ps
   ```

### Step 2: Install Python Dependencies

```bash
# Using Poetry
poetry add pydantic-ai asyncpg

# Or using pip
pip install pydantic-ai asyncpg
```

### Step 3: Configure Environment Variables (Optional)

The application uses default connection parameters, but you can customize them:

```bash
# Optional - set only if needed
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_NAME=bankdb
```

### Step 4: Run the Demo Application

```bash
# Using Poetry
poetry run python main.py

# Or directly with Python
python main.py
```

## Using pgAdmin

1. Open a web browser and navigate to: http://localhost:5050
2. Login with:

   - Email: admin@example.com
   - Password: admin

3. Add a new server:

   - Click "Add New Server"
   - On the "General" tab:
     - Name: BankDB
   - On the "Connection" tab:
     - Host: postgres (important: use the service name, not "localhost")
     - Port: 5432
     - Maintenance database: bankdb
     - Username: postgres
     - Password: postgres

4. Now you can browse the database, run queries, and manage tables.

## Database Schema

The database contains the following tables:

- **customers** - Customer information
- **accounts** - Bank accounts
- **transactions** - Transaction records
- **cards** - Bank cards

## Example Queries

The demo runs two example queries:

1. **Balance Inquiry**: "How much money do I have?"
2. **Lost Card Report**: "I lost my card!"

## Customizing the Agent

To modify the agent's behavior:

1. Edit the system prompt in `main.py`:

   ```python
   system_prompt=(
       'You are a bank customer support agent. Provide support to the customer '
       'and assess the risk level of their query. Use the customer\'s name in your response.'
   )
   ```

2. Add more tools by creating new functions with the `@support_agent.tool` decorator

## Shutting Down

When finished with the demo, stop the Docker containers:

```bash
docker-compose down
```

To remove all data, including the PostgreSQL database volume:

```bash
docker-compose down -v
```

## Troubleshooting

- **Connection Issues**: Ensure Docker containers are running
- **Database Errors**: Check connection parameters
- **SQL Errors**: Examine PostgreSQL logs with `docker logs bank-postgres`
