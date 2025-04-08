from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from pathlib import Path
from app.core.qa_chain import create_qa_chain
from app.core.pdf_processor import process_pdf

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

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-and-query")
async def upload_and_query(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    # Save the uploaded file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Process PDF and create QA chain
        processed_text = process_pdf(file_path)
        qa_chain = create_qa_chain(processed_text)
        
        # Get answer
        response = qa_chain.invoke({"question": question})
        
        return {
            "answer": response["answer"],
            "sources": response.get("sources", [])
        }
    finally:
        # Clean up the uploaded file
        if file_path.exists():
            file_path.unlink()

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 