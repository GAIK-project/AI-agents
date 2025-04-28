import logging

import psycopg
from langchain_huggingface import HuggingFaceEmbeddings
from psycopg.rows import dict_row

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection with dictionary row factory."""
    conn = psycopg.connect(
        "host=localhost port=5433 dbname=vector_db user=postgres password=postgres",
        row_factory=dict_row
    )
    return conn

def get_embeddings_model():
    """Initialize and return the embeddings model."""
    logger.info("Initializing embedding model...")
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def direct_vector_search(query_text, similarity_threshold=0.7, max_results=5, collection_name="tech_documents"):
    """
    Perform a direct vector search in the database without using a custom function.
    
    Args:
        query_text: The search query text
        similarity_threshold: Minimum similarity score (0-1)
        max_results: Maximum number of results to return
        collection_name: Name of the collection to search in
    
    Returns:
        List of document dictionaries with content, metadata, and similarity scores
    """
    # Get embeddings for the query
    embeddings_model = get_embeddings_model()
    query_embedding = embeddings_model.embed_query(query_text)
    
    try:
        conn = get_db_connection()
        logger.info(f"Checking database configuration...")
        
        # Check what collections are available
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM langchain_pg_collection")
            collections = [row['name'] for row in cur.fetchall()]
            logger.info(f"Available collections: {', '.join(collections)}")
            
            if not collections:
                logger.error("No collections found in the database.")
                logger.error("Please run the simple.py script first to create a collection and add documents.")
                return []
            
            if collection_name not in collections:
                logger.warning(f"Collection '{collection_name}' not found. Using '{collections[0]}' instead.")
                collection_name = collections[0]
        
        # Execute direct vector search
        logger.info(f"Executing direct vector search: '{query_text}' on collection '{collection_name}'")
        
        with conn.cursor() as cur:
            # For pgvector, we need to pass the vector as a string in the format '[1,2,3]'
            vector_str = str(query_embedding).replace('\n', '').replace(' ', '')
            
            # This direct SQL achieves the same result as our custom function would
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
            
            cur.execute(sql, (vector_str, collection_name, vector_str, similarity_threshold, vector_str, max_results))
            results = cur.fetchall()
        
        # Close connection
        conn.close()
        
        return results
    except Exception as e:
        logger.error(f"Error executing direct vector search: {e}")
        raise

def main():
    try:
        # Test the direct vector search
        query = "How do databases work?"
        logger.info(f"Searching for: '{query}'")
        
        results = direct_vector_search(
            query_text=query,
            similarity_threshold=0.1,  # Lower threshold to get more results
            max_results=5
        )
        
        # Display results
        print(f"\nResults for query: '{query}'\n")
        
        if not results:
            print("No results found matching the criteria.")
        else:
            for i, doc in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"Content: {doc['content']}")
                print(f"Similarity: {doc['similarity']:.4f} ({doc['similarity']*100:.1f}%)")
                print(f"Metadata: {doc['metadata']}")
                print("-" * 50)
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()