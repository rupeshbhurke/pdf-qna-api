import logging
import sys
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = "INFO",
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (default: INFO)
        log_format: Custom log format (optional)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set logging level
    level = getattr(logging, level.upper())
    logger.setLevel(level)
    
    # Default format includes timestamp, level, and message
    if not log_format:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance based on the environment.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get environment from .env file, default to development if not set
    env = os.getenv("APP_ENV", "development").lower()
    
    if env == "production":
        # Production: Log INFO and above to file
        logger = setup_logger(
            name=name,
            log_file="app.log",
            level="INFO"
        )
        logger.info(f"Logger initialized in PRODUCTION mode for {name}")
    else:
        # Development: Log DEBUG and above to console and file
        logger = setup_logger(
            name=name,
            log_file="debug.log",
            level="DEBUG",
            log_format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )
        logger.info(f"Logger initialized in DEVELOPMENT mode for {name}")
    
    return logger 