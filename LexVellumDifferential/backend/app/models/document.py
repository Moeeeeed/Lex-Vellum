from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.models.base import Base
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, default="Pending Review")  
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lawyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class DocumentCreate(BaseModel):
    text: str
    lawyer_id: Optional[int] = None
class DocumentUpdate(BaseModel):
    status: str
    comments: Optional[str] = None
class DocumentOut(BaseModel):
    id: int
    text: str
    status: str
    submitter_id: int
    lawyer_id: Optional[int] = None
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
