-- Create the extension pgvector (this is correct and needed)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for our example
CREATE SCHEMA IF NOT EXISTS pgvector_example;

-- Set search path to include our schema
SET search_path TO pgvector_example, public;

-- This leaves the search path pointing to the pgvector_example schema
ALTER DATABASE vector_db SET search_path TO pgvector_example, public;