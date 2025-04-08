from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
from pathlib import Path
from app.core.qa_chain import QAChain
from app.core.pdf_processor import pdf_processor
from app.core.qa_storage import qa_storage
from app.models.qa_history import QAHistoryResponse
from app.core.logger import get_logger
import shutil

logger = get_logger(__name__)

app = FastAPI(title="PDF Q&A API")

# Configure CORS
origins = [
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",  # Alternative localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directory for PDFs if it doesn't exist
STORAGE_DIR = Path("storage/pdfs")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"Storage directory initialized at {STORAGE_DIR}")

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    logger.info(f"Received upload request for {len(files)} files")
    uploaded_files = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Skipping non-PDF file: {file.filename}")
            continue
        
        file_path = STORAGE_DIR / file.filename
        try:
            logger.debug(f"Saving file: {file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append({
                "filename": file.filename,
                "path": str(file_path)
            })
            logger.info(f"Successfully uploaded: {file.filename}")
        except Exception as e:
            logger.error(f"Failed to upload {file.filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to upload {file.filename}")
    
    return {"uploaded_files": uploaded_files}

@app.get("/files")
async def list_files():
    logger.debug("Listing available PDF files")
    files = []
    for file_path in STORAGE_DIR.glob("*.pdf"):
        files.append({
            "filename": file_path.name,
            "path": str(file_path)
        })
    logger.debug(f"Found {len(files)} PDF files")
    return {"files": files}

@app.post("/query")
async def query_pdfs(question: str = Form(...)):
    logger.info(f"Received question: {question}")
    
    # Get content from all stored PDFs
    all_content = pdf_processor.get_all_pdf_content(STORAGE_DIR)
    
    if not all_content:
        logger.error("No PDF files found to analyze")
        raise HTTPException(status_code=400, detail="No PDF files found to analyze")
    
    # Create QA chain with combined content
    logger.debug("Creating QA chain")
    qa_chain = QAChain(all_content)
    
    # Get answer
    logger.debug("Generating answer")
    response = qa_chain.get_answer(question)
    
    # Get list of files used in the response
    source_files = [file.name for file in STORAGE_DIR.glob("*.pdf")]
    
    # Store QA record
    logger.debug("Storing QA record")
    qa_record = qa_storage.add_qa_record(
        question=question,
        answer=response["answer"],
        source_files=source_files
    )
    
    logger.info("Successfully generated answer")
    return {
        "answer": response["answer"],
        "sources": source_files,
        "qa_record": qa_record
    }

@app.get("/qa-history", response_model=QAHistoryResponse)
async def get_qa_history():
    """Get the history of questions and answers."""
    logger.debug("Retrieving QA history")
    history = qa_storage.get_qa_history()
    logger.debug(f"Retrieved {len(history)} QA records")
    return {"history": history}

@app.delete("/qa-history")
async def clear_qa_history():
    """Clear the QA history."""
    logger.warning("Clearing QA history")
    qa_storage.clear_history()
    logger.info("QA history cleared successfully")
    return {"message": "History cleared successfully"}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    logger.info(f"Request to delete file: {filename}")
    file_path = STORAGE_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path.unlink()
        logger.info(f"Successfully deleted file: {filename}")
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete {filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to delete {filename}")

@app.get("/health")
async def health_check():
    logger.debug("Health check request received")
    return {"status": "healthy"} 