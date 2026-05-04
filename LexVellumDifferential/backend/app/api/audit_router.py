from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.audit import AuditLog, AuditLogOut, BulkAuditLogCreate
from app.api.auth_router import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.post("/", response_model=List[AuditLogOut])
async def create_audit_logs(
    payload: BulkAuditLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    created_logs = []
    for log_data in payload.logs:
        new_log = AuditLog(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.email,
            action=log_data.action,
            original_text=log_data.original_text,
            new_text=log_data.new_text,
            legal_article=log_data.legal_article,
            full_document=log_data.full_document
        )
        db.add(new_log)
        created_logs.append(new_log)
    
    db.commit()
    for log in created_logs:
        db.refresh(log)
        
    return created_logs

@router.get("/", response_model=List[AuditLogOut])
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Depending on requirements, we could restrict this to CEO/Approver
    # For now, let's return all logs ordered by newest first.
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
