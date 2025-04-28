-- Create tables

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    account_number VARCHAR(20) UNIQUE,
    account_type VARCHAR(20) CHECK (account_type IN ('checking', 'savings', 'credit')),
    balance DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    amount DECIMAL(15, 2) NOT NULL,
    description VARCHAR(255),
    status VARCHAR(20) CHECK (status IN ('confirmed', 'pending', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cards table
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    card_number VARCHAR(20) UNIQUE,
    expiry_date DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('active', 'blocked', 'expired')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add test data

-- Test customers
INSERT INTO customers (id, name, email) 
VALUES 
    (123, 'John Smith', 'john.smith@example.com'),
    (124, 'Maria Garcia', 'maria.garcia@example.com'),
    (125, 'Ahmed Khan', 'ahmed.khan@example.com');

-- Test accounts
INSERT INTO accounts (customer_id, account_number, account_type, balance) 
VALUES 
    (123, 'ACC123456789', 'checking', 1000.00),
    (123, 'ACC123456790', 'savings', 5000.00),
    (124, 'ACC123456791', 'checking', 750.50),
    (125, 'ACC123456792', 'credit', -250.75);

-- Test transactions
INSERT INTO transactions (account_id, amount, description, status)
VALUES 
    (1, 100.00, 'Salary', 'confirmed'),
    (1, 23.45, 'Grocery Store', 'pending'),
    (1, -50.00, 'Restaurant', 'confirmed'),
    (2, 500.00, 'Deposit', 'confirmed'),
    (3, -125.50, 'Online Shopping', 'confirmed'),
    (4, -250.75, 'Credit Card Purchase', 'confirmed');

-- Test cards
INSERT INTO cards (account_id, card_number, expiry_date, status)
VALUES 
    (1, '1234-5678-9012-3456', '2026-12-31', 'active'),
    (3, '9876-5432-1098-7654', '2025-06-30', 'active'),
    (4, '1111-2222-3333-4444', '2024-09-30', 'active');