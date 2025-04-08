from PyPDF2 import PdfReader
from typing import List
import os

def process_pdf(file_path: str) -> str:
    """
    Process a PDF file and extract its text content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    reader = PdfReader(file_path)
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text 