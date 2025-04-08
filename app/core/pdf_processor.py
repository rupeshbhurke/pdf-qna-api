from PyPDF2 import PdfReader
from typing import List
import os
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger(__name__)

def process_pdf(file_path: str) -> str:
    """
    Process a single PDF file and extract its text content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    logger.debug(f"Processing PDF file: {file_path}")
    try:
        reader = PdfReader(file_path)
        text = ""
        
        for i, page in enumerate(reader.pages):
            logger.debug(f"Processing page {i+1} of {len(reader.pages)}")
            text += page.extract_text() + "\n"
        
        logger.info(f"Successfully processed PDF file: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error processing PDF file {file_path}: {str(e)}")
        raise

def get_all_pdf_content(directory: Path) -> str:
    """
    Get combined content from all PDF files in the specified directory.
    
    Args:
        directory: Path to directory containing PDF files
        
    Returns:
        str: Combined text from all PDFs, with clear separation between files
    """
    logger.debug(f"Scanning directory for PDFs: {directory}")
    all_content = []
    
    pdf_files = list(directory.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in directory")
    
    for pdf_file in pdf_files:
        try:
            logger.debug(f"Processing file: {pdf_file.name}")
            content = process_pdf(str(pdf_file))
            all_content.append(f"[File: {pdf_file.name}]\n{content}\n")
        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {str(e)}")
            continue
    
    return "\n---\n".join(all_content) 