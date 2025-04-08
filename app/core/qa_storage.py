import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import uuid
from app.models.qa_history import QARecord
from app.core.logger import get_logger

logger = get_logger(__name__)

class QAStorage:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.history_file = storage_dir / "qa_history.json"
        self._ensure_storage()
        logger.info(f"Initialized QA storage at {storage_dir}")
        
    def _ensure_storage(self):
        """Ensure storage directory and history file exist."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            if not self.history_file.exists():
                self.history_file.write_text("[]")
                logger.info("Created new QA history file")
            logger.debug("Storage directory and history file verified")
        except Exception as e:
            logger.error(f"Failed to ensure storage: {str(e)}")
            raise
            
    def _load_history(self) -> List[Dict]:
        """Load QA history from file."""
        try:
            logger.debug("Loading QA history from file")
            history = json.loads(self.history_file.read_text())
            logger.debug(f"Loaded {len(history)} QA records")
            return history
        except Exception as e:
            logger.error(f"Failed to load history: {str(e)}")
            return []
            
    def _save_history(self, history: List[Dict]):
        """Save QA history to file."""
        try:
            logger.debug(f"Saving {len(history)} QA records to file")
            self.history_file.write_text(json.dumps(history, default=str))
            logger.debug("Successfully saved QA history")
        except Exception as e:
            logger.error(f"Failed to save history: {str(e)}")
            raise
        
    def add_qa_record(self, question: str, answer: str, source_files: List[str]) -> QARecord:
        """Add a new QA record to history."""
        logger.debug(f"Adding new QA record for question: {question[:50]}...")
        history = self._load_history()
        
        new_record = {
            "id": str(uuid.uuid4()),
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow(),
            "source_files": source_files
        }
        
        history.append(new_record)
        self._save_history(history)
        
        logger.info(f"Added new QA record with ID: {new_record['id']}")
        return QARecord(**new_record)
        
    def get_qa_history(self) -> List[QARecord]:
        """Get all QA records."""
        logger.debug("Retrieving QA history")
        history = self._load_history()
        records = [QARecord(**record) for record in history]
        logger.debug(f"Retrieved {len(records)} QA records")
        return records
        
    def clear_history(self):
        """Clear all QA history."""
        logger.warning("Clearing all QA history")
        self._save_history([])
        logger.info("QA history cleared successfully")

# Create a global instance
qa_storage = QAStorage(Path("storage")) 