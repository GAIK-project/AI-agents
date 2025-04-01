import os

from dotenv import load_dotenv
from openai import OpenAI
from supabase import Client, create_client

# Load environment variables
load_dotenv()

# Get API keys from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Validate that environment variables are set
if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    missing = []
    if not SUPABASE_URL: missing.append("SUPABASE_URL")
    if not SUPABASE_KEY: missing.append("SUPABASE_KEY")
    if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
    raise ValueError(f"Missing environment variables: {', '.join(missing)}. Please set them in .env file or environment.")

# Initialize clients - note the new OpenAI client approach
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def search_documents(query: str, max_results: int = 5, similarity_threshold: float = 0.2):
    """Search for documents using vector similarity"""
    
    # 1. Get embedding for the query - using new client API
    embedding_response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    # The response structure has changed - it's now a Pydantic model
    query_embedding = embedding_response.data[0].embedding
    
    # 2. Use custom function to search for similar documents
    results = supabase.rpc(
        "find_similar_documents",
        {
            "query_embedding": query_embedding,
            "similarity_threshold": similarity_threshold,
            "max_results": max_results
        }
    ).execute()
    
    # 3. Print results
    print(f"Search query: '{query}'")
    print("-" * 50)
    
    if results.data:
        for i, doc in enumerate(results.data, 1):
            print(f"Result {i}: {doc.get('title', 'Untitled')} (Score: {doc['similarity']:.2f})")
            print(f"Content preview: {doc['content'][:150]}...")
            print("-" * 50)
    else:
        print("No matching documents found.")
    
    return results.data

# Example usage
if __name__ == "__main__":
    # Change this to any query related to Haaga-Helia reporting guidelines
    search_query = "How should I format my report?"
    search_documents(search_query)