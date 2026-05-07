from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.models.base import Base
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    original_text = Column(String, nullable=False)
    new_text = Column(String, nullable=False)
    legal_article = Column(String, nullable=True)
    full_document = Column(String, nullable=True)  
    document_id = Column(Integer, nullable=True) 
    timestamp = Column(DateTime, default=datetime.utcnow)
class AuditLogCreate(BaseModel):
    action: str
    original_text: str
    new_text: str
    legal_article: Optional[str] = None
    full_document: Optional[str] = None
    document_id: Optional[int] = None
class BulkAuditLogCreate(BaseModel):
    logs: List[AuditLogCreate]
class AuditLogOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    action: str
    original_text: str
    new_text: str
    legal_article: Optional[str] = None
    full_document: Optional[str] = None
    document_id: Optional[int] = None
    timestamp: datetime
    class Config:
        from_attributes = True
