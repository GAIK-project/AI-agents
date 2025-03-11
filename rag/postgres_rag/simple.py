import logging

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection string
POSTGRES_CONNECTION_STRING = "postgresql+psycopg://postgres:postgres@localhost:5433/vector_db"

def main():
    # Initialize embedding model
    logger.info("Initializing embedding model...")
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Set custom collection name - this is how you name your vector collection
    collection_name = "tech_documents"

    # Sample documents with metadata fields that we can later filter on
    logger.info(f"Creating collection '{collection_name}' with sample documents...")
    documents = [
        Document(
            page_content="Neural networks are a subset of machine learning models inspired by the human brain.",
            metadata={"category": "ML", "difficulty": "beginner", "year": 2022}
        ),
        Document(
            page_content="Transformers are a type of neural network architecture used primarily in NLP.",
            metadata={"category": "NLP", "difficulty": "intermediate", "year": 2022}
        ),
        Document(
            page_content="Vector databases store and retrieve high-dimensional vectors efficiently.",
            metadata={"category": "Databases", "difficulty": "intermediate", "year": 2023}
        ),
        Document(
            page_content="PostgreSQL is an open source relational database with pgvector extension for vector operations.",
            metadata={"category": "Databases", "difficulty": "beginner", "year": 2023}
        ),
    ]

    try:
        # Initialize the vector database with our documents
        vector_db = PGVector.from_documents(
            documents=documents,
            embedding=embeddings_model,
            collection_name=collection_name,  # Using our custom collection name
            connection=POSTGRES_CONNECTION_STRING,
            use_jsonb=True,
            # pre_delete_collection=True  # Uncomment to delete existing collection on each run
        )

        logger.info(f"Created or updated vector database with {len(documents)} documents")

        # -------------------------------------------------------
        # BASIC SEARCH WITHOUT FILTERING
        # -------------------------------------------------------
        query = "How do databases work?"
        logger.info(f"Executing basic query without filtering: '{query}'")

        basic_results = vector_db.similarity_search(query, k=4)
        print("\nBasic Search Results (no filtering):")
        for i, doc in enumerate(basic_results):
            print(f"\nResult {i+1}:")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print("-" * 50)

        # -------------------------------------------------------
        # SEARCH WITH FILTERING
        # -------------------------------------------------------
        # Filter example: only return documents in the "Databases" category 
        # that are at "beginner" difficulty level
        filter_condition = {
            "$and": [
                {"category": "Databases"},   # Documents must be in "Databases" category
                {"difficulty": "beginner"}   # AND have "beginner" difficulty
            ]
        }
        
        logger.info(f"Executing filtered query: {filter_condition}")
        
        filtered_results = vector_db.similarity_search(
            query, 
            k=4,  # Maximum number of results to return
            filter=filter_condition  # Apply our filter
        )
        
        print("\nFiltered Search Results (category=Databases AND difficulty=beginner):")
        for i, doc in enumerate(filtered_results):
            print(f"\nResult {i+1}:")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print("-" * 50)

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()