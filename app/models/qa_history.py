from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class QARecord(BaseModel):
    id: str  # UUID for the QA record
    question: str
    answer: str
    timestamp: datetime
    source_files: List[str]  # List of PDF filenames used to answer
    
class QAHistoryResponse(BaseModel):
    history: List[QARecord] 