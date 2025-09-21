from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import enum
import os
from dotenv import load_dotenv
from pathlib import Path

# Always load the .env that sits next to this file, regardless of CWD
# This prevents surprises when the server is started from the project root
# and ensures DATABASE_URL is read consistently.
load_dotenv(dotenv_path=Path(__file__).with_name('.env'))

# This will first check the .env file for the DATABASE_URL, if not found then it will use the default value given below
# Default uses SQLite for Railway deployment compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///task_management.db")

# It is like getting key to cabinet and opening it
# Force SQLite dialect to avoid MySQL detection issues
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

#  This is the session maker which is like a key to the cabinet
# and autocommit and autoflush is set to False so that the changes are not committed to the database until the session is committed and flushed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# blue print of database
Base = declarative_base()

# This is the enum for the status of the task
class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# This is the enum for the priority of the task
class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# This is the model for the task
class Task(Base): # 
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
