"""
Multimodal RAG System with IBM Docling and Granite

This script implements a multimodal retrieval-augmented generation (RAG) system
using IBM's Docling and Granite models to process and analyze PDF documents.
"""

import argparse
import base64
import io
import itertools
import logging
import os
import sys
from typing import Dict, List

import PIL.Image
import PIL.ImageOps
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.doc.document import RefItem, TableItem
from docling_core.types.doc.labels import DocItemLabel
from dotenv import load_dotenv
from ibm_granite_community.notebook_utils import get_env_var
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Replicate
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoProcessor, AutoTokenizer

# Load environment variables from .env file
load_dotenv()


def check_prerequisites():
    """Verify that Python version is compatible with the requirements."""
    assert sys.version_info >= (3, 10), "Use Python 3.10 or newer to run this script."
    assert os.getenv("REPLICATE_API_TOKEN"), "REPLICATE_API_TOKEN environment variable is required"


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def encode_image(image: PIL.Image.Image, format: str = "png") -> str:
    """Encode an image to a base64 data URI."""
    image = PIL.ImageOps.exif_transpose(image) or image
    image = image.convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format)
    encoding = base64.b64encode(buffer.getvalue()).decode("utf-8")
    uri = f"data:image/{format};base64,{encoding}"
    return uri


class MultimodalRAGSystem:
    """A multimodal RAG system using IBM's Docling and Granite models."""

    def __init__(self, force_reprocess=False):
        self.logger = logging.getLogger(__name__)
        self.document_converter = None
        self.embeddings_model = None
        self.embeddings_tokenizer = None
        self.vision_model = None
        self.vision_processor = None
        self.language_model = None
        self.language_tokenizer = None
        self.vector_db = None
        self.rag_chain = None
        self.force_reprocess = force_reprocess
        self.db_dir = os.path.join(os.getcwd(), "database")
        
    def initialize_models(self):
        """Initialize all AI models needed for the RAG system."""
        self.logger.info("Initializing AI models...")
        
        # Initialize embeddings model
        embeddings_model_path = "ibm-granite/granite-embedding-30m-english"
        self.embeddings_model = HuggingFaceEmbeddings(
            model_name=embeddings_model_path,
        )
        self.embeddings_tokenizer = AutoTokenizer.from_pretrained(embeddings_model_path)
        
        # Initialize vision model
        vision_model_path = "ibm-granite/granite-vision-3.2-2b"
        self.vision_model = Replicate(
            model=vision_model_path,
            replicate_api_token=get_env_var("REPLICATE_API_TOKEN"),
            model_kwargs={
                "max_tokens": self.embeddings_tokenizer.max_len_single_sentence,
                "min_tokens": 100,
            },
        )
        self.vision_processor = AutoProcessor.from_pretrained(vision_model_path)
        
        # Initialize language model
        language_model_path = "ibm-granite/granite-3.2-8b-instruct"
        self.language_model = Replicate(
            model=language_model_path,
            replicate_api_token=get_env_var("REPLICATE_API_TOKEN"),
            model_kwargs={
                "max_tokens": 1000,
                "min_tokens": 100,
            },
        )
        self.language_tokenizer = AutoTokenizer.from_pretrained(language_model_path)
        
        self.logger.info("AI models initialized successfully")

    def initialize_document_converter(self):
        """Initialize the Docling document converter."""
        self.logger.info("Initializing document converter...")
        
        pdf_pipeline_options = PdfPipelineOptions(
            do_ocr=False,
            generate_picture_images=True,
        )
        format_options = {
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_pipeline_options),
        }
        self.document_converter = DocumentConverter(format_options=format_options)
        
        self.logger.info("Document converter initialized successfully")

    def initialize_vector_db(self):
        """Initialize the vector database for storing document embeddings."""
        self.logger.info("Initializing vector database...")
        
        # Create database directory if it doesn't exist
        os.makedirs(self.db_dir, exist_ok=True)
        self.logger.info(f"The vector database is stored in {self.db_dir}")
        
        # Initialize the ChromaDB vector store
        self.vector_db = Chroma(
            embedding_function=self.embeddings_model,
            persist_directory=self.db_dir
        )
        
        # Check if the database already has documents
        try:
            collection_size = len(self.vector_db.get()["ids"])
            self.logger.info(f"Found existing database with {collection_size} documents")
            # If we're not forcing reprocessing and there are documents, we can skip the document processing
            if collection_size > 0 and not self.force_reprocess:
                self.logger.info("Using existing database. To reprocess, use --force-reprocess flag")
                return True
            elif self.force_reprocess and collection_size > 0:
                self.logger.info("Force reprocessing requested. Clearing existing database...")
                self.vector_db = Chroma(
                    embedding_function=self.embeddings_model,
                    persist_directory=self.db_dir,
                    collection_name="langchain",
                    collection_metadata={"hnsw:space": "cosine"}
                )
        except Exception as e:
            self.logger.info(f"No existing database found or error accessing it: {e}")
        
        self.logger.info("Vector database initialized successfully")
        return False

    def process_documents(self, sources: List[str]) -> Dict[str, Dict]:
        """Process documents from the provided sources."""
        self.logger.info(f"Processing documents from {len(sources)} sources...")
        
        # Convert documents using Docling
        conversions = {
            source: self.document_converter.convert(source=source).document
            for source in sources
        }
        
        self.logger.info("Documents converted successfully")
        return conversions

    def extract_text_chunks(self, conversions: Dict[str, Dict]) -> List[Document]:
        """Extract and chunk text content from the converted documents."""
        self.logger.info("Extracting text chunks...")
        
        doc_id = 0
        texts = []
        
        for source, docling_document in conversions.items():
            for chunk in HybridChunker(tokenizer=self.embeddings_tokenizer).chunk(docling_document):
                items = chunk.meta.doc_items
                if len(items) == 1 and isinstance(items[0], TableItem):
                    continue  # Process tables separately
                    
                refs = " ".join(map(lambda item: item.get_ref().cref, items))
                text = chunk.text
                
                document = Document(
                    page_content=text,
                    metadata={
                        "doc_id": doc_id + 1,
                        "source": source,
                        "ref": refs,
                    },
                )
                texts.append(document)
                doc_id += 1
        
        self.logger.info(f"{len(texts)} text document chunks created")
        return texts

    def extract_tables(self, conversions: Dict[str, Dict], start_doc_id: int) -> List[Document]:
        """Extract tables from the converted documents."""
        self.logger.info("Extracting tables...")
        
        doc_id = start_doc_id
        tables = []
        
        for source, docling_document in conversions.items():
            for table in docling_document.tables:
                if table.label in [DocItemLabel.TABLE]:
                    ref = table.get_ref().cref
                    text = table.export_to_markdown()
                    
                    document = Document(
                        page_content=text,
                        metadata={
                            "doc_id": doc_id + 1,
                            "source": source,
                            "ref": ref,
                        },
                    )
                    tables.append(document)
                    doc_id += 1
        
        self.logger.info(f"{len(tables)} table documents created")
        return tables

    def process_images(self, conversions: Dict[str, Dict], start_doc_id: int) -> List[Document]:
        """Process images from the converted documents using the vision model."""
        self.logger.info("Processing images...")
        
        doc_id = start_doc_id
        pictures = []
        
        # Prepare vision model prompt
        image_prompt = "If the image contains text, explain the text in the image."
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": image_prompt},
                ],
            },
        ]
        vision_prompt = self.vision_processor.apply_chat_template(
            conversation=conversation,
            add_generation_prompt=True,
        )
        
        for source, docling_document in conversions.items():
            for picture in docling_document.pictures:
                ref = picture.get_ref().cref
                self.logger.info(f"Processing image: {ref}")
                
                image = picture.get_image(docling_document)
                if image:
                    text = self.vision_model.invoke(vision_prompt, image=encode_image(image))
                    
                    document = Document(
                        page_content=text,
                        metadata={
                            "doc_id": doc_id + 1,
                            "source": source,
                            "ref": ref,
                        },
                    )
                    pictures.append(document)
                    doc_id += 1
        
        self.logger.info(f"{len(pictures)} image descriptions created")
        return pictures

    def populate_vector_db(self, documents: List[Document]):
        """Add documents to the vector database."""
        self.logger.info("Adding documents to vector database...")
        self.vector_db.add_documents(documents)
        # Persist the database to disk
        if hasattr(self.vector_db, "_persist"):
            self.vector_db._persist()
        self.logger.info(f"{len(documents)} documents added to the vector database")

    def create_rag_pipeline(self):
        """Create the RAG pipeline using LangChain and Granite models."""
        self.logger.info("Creating RAG pipeline...")
        
        # Create prompt templates
        prompt = self.language_tokenizer.apply_chat_template(
            conversation=[{
                "role": "user",
                "content": "{input}",
            }],
            documents=[{
                "title": "placeholder",
                "text": "{context}",
            }],
            add_generation_prompt=True,
            tokenize=False,
        )
        prompt_template = PromptTemplate.from_template(template=prompt)
        
        # Create document prompt template
        document_prompt_template = PromptTemplate.from_template(template="""\
Document {doc_id}
{page_content}""")
        document_separator = "\n\n"
        
        # Assemble the RAG chain
        combine_docs_chain = create_stuff_documents_chain(
            llm=self.language_model,
            prompt=prompt_template,
            document_prompt=document_prompt_template,
            document_separator=document_separator,
        )
        
        self.rag_chain = create_retrieval_chain(
            retriever=self.vector_db.as_retriever(),
            combine_docs_chain=combine_docs_chain,
        )
        
        self.logger.info("RAG pipeline created successfully")

    def test_retrieval(self, query: str):
        """Test retrieval from the vector database."""
        self.logger.info(f"Testing retrieval with query: {query}")
        for doc in self.vector_db.as_retriever().invoke(query):
            print(doc)
            print("=" * 80)

    def answer_query(self, query: str) -> str:
        """Answer a query using the RAG pipeline."""
        self.logger.info(f"Answering query: {query}")
        outputs = self.rag_chain.invoke({"input": query})
        return outputs["answer"]

    def run(self, sources: List[str], query: str):
        """Run the complete RAG pipeline."""
        # Initialize all components
        self.initialize_models()
        
        # Initialize vector database and check if we need to process documents
        use_existing_db = self.initialize_vector_db()
        
        if not use_existing_db:
            self.initialize_document_converter()
            
            # Process documents
            conversions = self.process_documents(sources)
            
            # Extract content
            text_chunks = self.extract_text_chunks(conversions)
            tables = self.extract_tables(conversions, len(text_chunks))
            pictures = self.process_images(conversions, len(text_chunks) + len(tables))
            
            # Combine all documents
            all_documents = list(itertools.chain(text_chunks, tables, pictures))
            
            # Add to vector database
            self.populate_vector_db(all_documents)
        
        # Create RAG pipeline
        self.create_rag_pipeline()
        
        # Use the query to get an answer
        answer = self.answer_query(query)
        print("\nAnswer:")
        print(answer)


def main():
    """Main function to run the multimodal RAG system."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Multimodal RAG System")
    parser.add_argument("--force-reprocess", action="store_true", 
                        help="Force reprocessing of documents even if database exists")
    args = parser.parse_args()
    
    # Check prerequisites
    check_prerequisites()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Multimodal RAG System")
    
    # Define document sources
    sources = [
        "https://midwestfoodbank.org/images/AR_2020_WEB2.pdf",
    ]
    
    # Define query here - easy to change for different questions
    query = "How did the COVID-19 pandemic affect the amount of donations in 2020?"
    
    # Create and run the RAG system
    rag_system = MultimodalRAGSystem(force_reprocess=args.force_reprocess)
    rag_system.run(sources, query)
    
    logger.info("Multimodal RAG System completed successfully")


if __name__ == "__main__":
    main()
    
# Questions for app
# 1. How did MFB manage to distribute $383 million worth of food by spending only $13 million?
# 2. What was the percentage of MFB's administrative costs compared to total expenses, and how does it compare to similar organizations?
# 3. How did the COVID-19 pandemic affect the amount of donations in 2020?

# Operational questions
# 4. How did food distribution change during the pandemic?
# 5. What was the significance of the USDA Farmers to Families program for MFB's operations?
# 6. Why did the production of Tender Mercies meals increase so significantly in 2020?

# Growth-related questions
# 7. Why did MFB open two new locations (Pennsylvania and New England) during the pandemic?
# 8. How has the value of food distributed by MFB developed since its founding in 2003?

# Volunteer-related questions
# 9. How does MFB manage to operate with such a small paid staff (450 volunteers per paid employee)?
# 10. How did the National Guard assistance affect MFB's operations during the pandemic?

# Disaster relief questions
# 11. How did MFB's disaster relief change in 2020 compared to normal years?
# 12. Where was food aid delivered during the COVID-19 pandemic?

# International operations questions
# 13. How does the operation in East Africa and Haiti differ from the U.S. operations?
# 14. What specific challenges did the international locations face during the pandemic?