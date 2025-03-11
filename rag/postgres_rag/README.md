# Simple PgVector Example

A simplified example demonstrating how to use PostgreSQL with pgvector for vector storage and retrieval using LangChain.

## Features

- Store document embeddings in PostgreSQL using pgvector extension
- Perform semantic similarity searches on your documents
- Filter search results using document metadata
- Use custom collection names to organize different document sets
- Efficient metadata storage using JSONB format

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Internet connection (for downloading embedding models)

## Setup

1. Start the PostgreSQL database with pgvector:

```bash
docker-compose up -d
```

2. Install Python dependencies:

```bash
pip install langchain-postgres langchain-huggingface psycopg
```

3. Run the example:

```bash
python simple.py
```

## How it Works

1. **Database Setup**: The Docker Compose file sets up PostgreSQL with the pgvector extension

2. **Document Processing**: Documents with text content and metadata are embedded using a language model

3. **Vector Storage**: The document embeddings are stored in PostgreSQL:

   - Embeddings are stored as vector data types in PostgreSQL
   - Metadata is stored in JSONB format for efficient querying
   - Documents are organized in collections with custom names

4. **Similarity Search**: You can query the database to find semantically similar documents:
   - Basic search returns documents most similar to your query
   - Filtered search lets you combine semantic similarity with metadata conditions

## Example Usage

### Basic Similarity Search

```python
# Simple query without filtering
results = vector_db.similarity_search("How do neural networks work?", k=2)
```

### Filtered Similarity Search

```python
# Filter by category and difficulty level
filter_condition = {
    "$and": [
        {"category": "Databases"},
        {"difficulty": "beginner"}
    ]
}

filtered_results = vector_db.similarity_search(
    "How do databases work?",
    k=4,
    filter=filter_condition
)
```

## Filtering Options

PGVector supports a variety of filtering operators:

- `$eq`, `$ne`: Equality/inequality (==, !=)
- `$lt`, `$lte`, `$gt`, `$gte`: Comparisons (<, <=, >, >=)
- `$in`, `$nin`: Membership in a list
- `$and`, `$or`: Logical operators
- `$like`, `$ilike`: Text pattern matching
- `$between`: Range check

## Project Structure

- `docker-compose.yml`: Sets up PostgreSQL with pgvector and pgAdmin
- `init-db.sql`: Database initialization script
- `simple.py`: Main Python script demonstrating vector storage and retrieval

## Troubleshooting

- If connection fails, ensure the database is running: `docker-compose ps`
- Access pgAdmin at http://localhost:5050 to inspect the database (email: admin@example.com, password: admin)
- If you encounter schema errors, check that init-db.sql was executed properly
- Make sure pgvector extension is properly installed in your PostgreSQL container
