# Multimodal RAG System with IBM Docling and Granite

This script implements a multimodal retrieval-augmented generation (RAG) system
using IBM's Docling and Granite models to process and analyze PDF documents.

The system performs the following steps:

1. Processes PDF documents using Docling to extract text, tables, and images
2. Processes images using IBM Granite Vision to extract text and content
3. Creates vector embeddings of all content using IBM Granite Embeddings
4. Stores the vectors in a ChromaDB vector database
5. Creates a RAG pipeline using IBM Granite language model
6. Answers user queries based on the document content

## Setup

1. Clone the repository
2. Rename `.env.example` to `.env` and add your Replicate API token:
   ```
   cp .env.example .env
   ```
3. Edit the `.env` file and replace `your_replicate_api_token_here` with your actual Replicate API token
4. Install dependencies using Poetry or pip (see below)

## Usage

```bash
# Basic usage - uses existing database if available
python main.py

# Force reprocessing of documents even if database exists
python main.py --force-reprocess
```

The system uses a default query defined in the `main()` function. You can easily change this by modifying the `query` variable in `main.py` to ask different questions about the document.

## Requirements

- Python 3.10 or newer
- REPLICATE_API_TOKEN environment variable set with your API token
- Required packages installed (see pyproject.toml or requirements.txt)

## Database

The system stores processed documents in a ChromaDB vector database in the `database` directory. This allows reusing the database for subsequent queries without reprocessing documents and making additional API calls.

## Based on IBM Tutorial

This implementation is based on the IBM Granite tutorial for building a multimodal RAG system:

- [IBM Tutorial: Build an AI-powered multimodal RAG system with Docling and Granite](https://www.ibm.com/think/tutorials/build-multimodal-rag-langchain-with-docling-granite)
- [GitHub: Granite Snack Cookbook - Multimodal RAG Recipe](https://github.com/ibm-granite-community/granite-snack-cookbook/blob/main/recipes/RAG/Granite_Multimodal_RAG.ipynb)

The main modifications include:

1. Using ChromaDB instead of Milvus for better Windows compatibility
2. Adding persistent database storage in a visible location
3. Adding command-line arguments for easier usage
4. Checking for existing database to avoid unnecessary reprocessing

The core RAG functionality follows the same approach as the original IBM implementation.
