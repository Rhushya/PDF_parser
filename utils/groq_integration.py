import os
from typing import List, Dict, Any
from llama_index import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.node_parser import SimpleNodeParser
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqPDFQuery:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize Groq LLM
        self.llm = Groq(api_key=api_key)
        
        # Initialize HuggingFace Embeddings with CPU-only configuration
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            device="cpu"  # Force CPU usage
        )
        
        # Configure Settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 512
        
        self.index = None

    def create_index(self, documents_dir: str) -> None:
        """Create a vector index from the parsed PDF documents"""
        try:
            # Load documents
            documents = SimpleDirectoryReader(documents_dir).load_data()
            
            # Parse nodes
            parser = SimpleNodeParser.from_defaults()
            nodes = parser.get_nodes_from_documents(documents)
            
            # Create index
            self.index = VectorStoreIndex(nodes)
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise

    def query(self, question: str) -> str:
        """Query the PDF content using Groq"""
        if not self.index:
            raise ValueError("Index not created. Call create_index() first.")
        
        try:
            # Create query engine with specific configuration
            query_engine = self.index.as_query_engine(
                similarity_top_k=3,
                response_mode="compact"
            )
            
            # Get response
            response = query_engine.query(question)
            return str(response)
            
        except Exception as e:
            logger.error(f"Error querying: {str(e)}")
            raise 