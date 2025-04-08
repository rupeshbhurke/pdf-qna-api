import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.core.logger import get_logger

logger = get_logger(__name__)

class LLMProvider:
    """A class to manage LLM configuration and initialization."""
    
    def __init__(self):
        """Initialize the LLM provider with configuration from environment variables."""
        load_dotenv()
        self._configure()
        self.llm = self._initialize_llm()
        logger.info("LLMProvider initialized successfully")
    
    def _configure(self):
        """Configure LLM parameters from environment variables."""
        self.llm_params = {
            "model": os.environ.get("MODEL_NAME", "gpt-4o-az"),
            "openai_api_base": os.environ.get("OPENAI_API_BASE"),
            "api_key": os.environ.get("LLAMA_API_KEY"),
            "temperature": 0.0
        }
        logger.debug("LLM parameters configured")
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize and return the LLM instance."""
        try:
            llm = ChatOpenAI(**self.llm_params)
            logger.debug("LLM instance initialized successfully")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def get_llm(self) -> ChatOpenAI:
        """Get the configured LLM instance."""
        return self.llm

# Create a global instance
llm_provider = LLMProvider()
llm = llm_provider.get_llm()




