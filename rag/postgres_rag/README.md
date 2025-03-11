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

One of the most powerful features of PGVector is the ability to combine semantic similarity search with metadata filtering. This means you can search for documents that are both semantically similar to your query and match specific metadata criteria.

### Available Filtering Operators

PGVector supports a variety of filtering operators that can be applied to any metadata field:

- `$eq`, `$ne`: Equality/inequality (==, !=)
- `$lt`, `$lte`, `$gt`, `$gte`: Comparisons (<, <=, >, >=)
- `$in`, `$nin`: Membership in a list
- `$between`: Range check between two values
- `$like`, `$ilike`: Text pattern matching (case-sensitive and case-insensitive)
- `$and`, `$or`: Logical operators for combining conditions

### Filtering Examples

**Simple equality filter:**

```python
# Find documents about databases that were published in 2023
filter_condition = {
    "category": "Databases",
    "year": 2023
}
```

**Using comparison operators:**

```python
# Find documents with page number greater than 50
filter_condition = {
    "page": {"$gt": 50}
}
```

**Using IN operator for multiple possible values:**

```python
# Find documents in either the ML or NLP categories
filter_condition = {
    "category": {"$in": ["ML", "NLP"]}
}
```

**Range filtering with BETWEEN:**

```python
# Find documents published between 2020 and 2023
filter_condition = {
    "year": {"$between": [2020, 2023]}
}
```

**Text pattern matching:**

```python
# Find documents where source contains "text"
filter_condition = {
    "source": {"$ilike": "%text%"}
}
```

**Complex logical combinations:**

```python
# Find beginner-level documents from 2023 OR any advanced documents
filter_condition = {
    "$or": [
        {
            "$and": [
                {"difficulty": "beginner"},
                {"year": 2023}
            ]
        },
        {"difficulty": "advanced"}
    ]
}
```

### No Custom SQL Functions Needed

With LangChain's PGVector implementation, you don't need to write any custom SQL functions to perform these filters. The library automatically converts these filter conditions into efficient SQL queries behind the scenes, combining them with vector similarity search operations.

## Advanced Vector Search Options

pgvector offers powerful ways to query your vector database beyond basic similarity search through LangChain. This section covers how to perform custom vector queries for more control and flexibility.

### Direct Vector Queries

For more control over your vector searches, you can use direct SQL queries against the PostgreSQL database:

```python
# direct_vector_search.py
from langchain_huggingface import HuggingFaceEmbeddings
import psycopg
from psycopg.rows import dict_row

def direct_vector_search(query_text, similarity_threshold=0.3, max_results=5):
    # Initialize embedding model
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Convert query to embedding vector
    query_embedding = embeddings_model.embed_query(query_text)

    # Connect to database
    conn = psycopg.connect(
        "host=localhost port=5433 dbname=vector_db user=postgres password=postgres",
        row_factory=dict_row
    )

    # Execute direct vector search
    with conn.cursor() as cur:
        # Format vector for PostgreSQL
        vector_str = str(query_embedding).replace('\n', '').replace(' ', '')

        # Direct SQL query with pgvector
        sql = """
        SELECT
            e.id::text as id,
            e.document as content,
            e.cmetadata as metadata,
            1 - (e.embedding <=> %s::vector) as similarity
        FROM
            langchain_pg_embedding e
        JOIN
            langchain_pg_collection c ON e.collection_id = c.uuid
        WHERE
            c.name = %s
            AND 1 - (e.embedding <=> %s::vector) > %s
        ORDER BY
            e.embedding <=> %s::vector
        LIMIT %s
        """

        cur.execute(sql, (
            vector_str,           # Query vector
            "tech_documents",     # Collection name
            vector_str,           # Query vector (again for WHERE clause)
            similarity_threshold, # Minimum similarity score
            vector_str,           # Query vector (again for ORDER BY)
            max_results           # Maximum results to return
        ))

        results = cur.fetchall()

    conn.close()
    return results
```

### Tuning Similarity Threshold

The similarity threshold determines how closely documents must match your query:

- **Higher threshold** (e.g., 0.8): Only returns very similar documents, might yield fewer results
- **Medium threshold** (e.g., 0.5): Balances precision and recall
- **Lower threshold** (e.g., 0.3 or 0.1): Returns more documents, including less similar ones

Experiment with different thresholds based on your specific data and needs.

### Creating Custom Database Functions

For reusable vector search logic, you can create a custom PostgreSQL function directly in your database:

1. **Connect to your database** using pgAdmin or psql

2. **Create the function**:

```sql
CREATE OR REPLACE FUNCTION pgvector_example.match_documents(
    query_embedding vector(384),  -- Adjust dimension size if needed
    match_threshold float,
    match_count int,
    collection_name text
)
RETURNS TABLE (
    id text,
    content text,
    metadata jsonb,
    similarity float
) AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        e.id::text,
        e.document as content,
        e.cmetadata as metadata,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM
        langchain_pg_embedding e
    JOIN
        langchain_pg_collection c ON e.collection_id = c.uuid
    WHERE
        c.name = collection_name
        AND 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY
        e.embedding <=> query_embedding
    LIMIT match_count;
END;
$BODY$ LANGUAGE plpgsql;
```

3. **Call the function from Python**:

```python
def call_custom_database_function(query_text, threshold=0.3, max_results=5):
    # Get query embedding
    embeddings_model = get_embeddings_model()
    query_embedding = embeddings_model.embed_query(query_text)
    vector_str = str(query_embedding).replace('\n', '').replace(' ', '')

    # Connect to database
    conn = psycopg.connect(
        "host=localhost port=5433 dbname=vector_db user=postgres password=postgres",
        row_factory=dict_row
    )

    # Call the custom function
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM pgvector_example.match_documents(%s, %s, %s, %s)",
            (vector_str, threshold, max_results, "tech_documents")
        )
        results = cur.fetchall()

    conn.close()
    return results
```

### Benefits of Direct SQL and Custom Functions

- **Greater flexibility**: Fine-tune queries beyond LangChain's interface
- **Performance optimizations**: Add custom indexes or filtering logic
- **Specialized queries**: Implement custom distance metrics or scoring
- **Reusability**: Use the same search logic from different applications

## Project Structure

- `docker-compose.yml`: Sets up PostgreSQL with pgvector and pgAdmin
- `init-db.sql`: Database initialization script
- `simple.py`: Main Python script demonstrating vector storage and retrieval
- `direct_vector_query.py`: Example of direct SQL vector queries

## Troubleshooting

- If connection fails, ensure the database is running: `docker-compose ps`
- Access pgAdmin at <http://localhost:5050> to inspect the database (email: <admin@example.com>, password: admin)
- If you encounter schema errors, check that init-db.sql was executed properly
- Make sure pgvector extension is properly installed in your PostgreSQL container
- For similarity issues, try lowering the similarity threshold (e.g., from 0.7 to 0.3)
