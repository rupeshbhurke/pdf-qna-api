# PDF Q&A System

A web application that allows users to upload PDF files and ask questions about their content. The system uses LangGraph's Plan & Execute pattern to provide accurate answers based on the PDF content.

## Features

- PDF file upload
- Question answering based on PDF content
- Modern and responsive UI
- Plan & Execute pattern for accurate answers

## Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key

## Setup

1. Clone the repository
2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Backend Setup

1. Navigate to the project root directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Upload a PDF file
3. Enter your question about the PDF content
4. Click "Get Answer" to receive a response

## Architecture

The system uses a two-part architecture:

1. **Backend (FastAPI)**:
   - Handles file uploads
   - Processes PDF content
   - Implements LangGraph's Plan & Execute pattern
   - Provides REST API endpoints

2. **Frontend (React)**:
   - Modern UI built with Material-UI
   - File upload interface
   - Question input form
   - Answer display

## License

MIT 