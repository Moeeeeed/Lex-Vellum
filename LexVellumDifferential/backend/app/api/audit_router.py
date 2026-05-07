from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.audit import AuditLog, AuditLogOut, BulkAuditLogCreate, AuditLogCreate
from app.api.auth_router import get_current_user, check_role
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
            full_document=log_data.full_document,
            document_id=log_data.document_id
        )
        db.add(new_log)
        created_logs.append(new_log)
    db.commit()
    for log in created_logs:
        db.refresh(log)
    return created_logs
@router.get("/", response_model=List[AuditLogOut])
async def get_audit_logs(
    current_user: User = Depends(check_role(["CEO", "Approver"])),
    db: Session = Depends(get_db),
    document_id: int = None
):
    query = db.query(AuditLog)
    if document_id:
        query = query.filter(AuditLog.document_id == document_id)
    return query.order_by(AuditLog.timestamp.desc()).all()
@router.post("/commit_remediation", response_model=AuditLogOut)
async def commit_remediation(
    payload: AuditLogCreate,
    current_user: User = Depends(check_role(["CEO", "Editor", "Approver"])),
    db: Session = Depends(get_db)
):
    new_log = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        action=f"Accepted Remediation: {payload.action}",
        original_text=payload.original_text,
        new_text=payload.new_text,
        legal_article=payload.legal_article,
        full_document=payload.full_document,
        document_id=payload.document_id
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log
