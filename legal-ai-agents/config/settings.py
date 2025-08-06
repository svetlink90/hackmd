"""
Configuration settings for Legal Research AI Agents
"""
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    CACHE_DIR = PROJECT_ROOT / "cache"
    
    # AI Service Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///legal_research.db")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")
    
    # Legal Database APIs
    WESTLAW_API_KEY = os.getenv("WESTLAW_API_KEY")
    LEXISNEXIS_API_KEY = os.getenv("LEXISNEXIS_API_KEY")
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "pdf,docx,txt,md").split(",")
    
    # Web Interface
    FLASK_HOST = os.getenv("FLASK_HOST", "localhost")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    
    # Processing Settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Legal Research Prompts
    LEGAL_ANALYSIS_PROMPT = """
    You are an expert legal research assistant. Analyze the provided legal document and:
    1. Identify key legal concepts and terms
    2. Extract important clauses and provisions
    3. Highlight potential legal issues or concerns
    4. Summarize the main points in clear, professional language
    5. Suggest areas for further research if applicable
    
    Document to analyze:
    {document_text}
    
    Please provide a structured analysis.
    """
    
    CASE_LAW_RESEARCH_PROMPT = """
    You are conducting legal research. Based on the query below, provide:
    1. Relevant legal principles
    2. Key cases to research (if known)
    3. Jurisdictional considerations
    4. Search terms for further research
    5. Potential legal arguments
    
    Research Query: {query}
    
    Provide a comprehensive research starting point.
    """
    
    CONTRACT_ANALYSIS_PROMPT = """
    Analyze this contract and provide:
    1. Contract type and purpose
    2. Key parties and their obligations
    3. Important terms and conditions
    4. Potential risks or red flags
    5. Missing clauses or provisions
    6. Recommendations for review
    
    Contract text:
    {contract_text}
    """

# Create directories if they don't exist
def ensure_directories():
    """Create necessary directories"""
    for directory in [Settings.DATA_DIR, Settings.LOGS_DIR, Settings.CACHE_DIR]:
        directory.mkdir(exist_ok=True)

# Legal document types and their characteristics
LEGAL_DOCUMENT_TYPES = {
    "contract": {
        "keywords": ["agreement", "contract", "terms", "conditions", "obligations"],
        "analysis_focus": ["parties", "obligations", "terms", "conditions", "termination"]
    },
    "statute": {
        "keywords": ["section", "subsection", "code", "statute", "law"],
        "analysis_focus": ["requirements", "definitions", "penalties", "scope"]
    },
    "case_law": {
        "keywords": ["court", "judge", "plaintiff", "defendant", "holding"],
        "analysis_focus": ["facts", "issue", "holding", "reasoning", "precedent"]
    },
    "regulation": {
        "keywords": ["regulation", "rule", "cfr", "federal register"],
        "analysis_focus": ["requirements", "compliance", "definitions", "enforcement"]
    }
}

# Initialize settings
settings = Settings()
ensure_directories()