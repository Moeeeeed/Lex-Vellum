from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.document import Document, DocumentCreate, DocumentOut, DocumentUpdate
from app.models.user import User
from app.api.auth_router import get_current_user, check_role
from app.services.email_service import send_email
from app.models.audit import AuditLog

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/", response_model=DocumentOut)
async def submit_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only CEO or Editor can submit
    if current_user.role not in ["CEO", "Editor"]:
        raise HTTPException(status_code=403, detail="Only CEO or Editor can submit documents.")

    # Find the assigned lawyer (if not provided, default to the first Approver)
    lawyer_id = payload.lawyer_id
    if not lawyer_id:
        lawyer = db.query(User).filter(User.role == "Approver").first()
        if lawyer:
            lawyer_id = lawyer.id
        else:
            print("Warning: No Approver found to assign the document to.")

    new_doc = Document(
        text=payload.text,
        status="Pending Review",
        submitter_id=current_user.id,
        lawyer_id=lawyer_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Email notification
    if lawyer_id:
        lawyer_user = db.query(User).filter(User.id == lawyer_id).first()
        if lawyer_user:
            email_body = f"""
Hello {lawyer_user.full_name or 'Lawyer'},

A new legal document has been finalized and submitted by {current_user.full_name or 'the CEO'}.
It is now awaiting your final review and approval.

Please log in to LexVellum Differential to review the document and the Audit Trail.

Best regards,
LexVellum Automated System
"""
            send_email(lawyer_user.email, "Action Required: Document Ready for Legal Review", email_body)

    return new_doc

@router.get("/", response_model=List[DocumentOut])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "CEO":
        return db.query(Document).order_by(Document.created_at.desc()).all()
    elif current_user.role == "Approver":
        return db.query(Document).filter(Document.lawyer_id == current_user.id).order_by(Document.created_at.desc()).all()
    else:
        # Editors can see their own
        return db.query(Document).filter(Document.submitter_id == current_user.id).order_by(Document.created_at.desc()).all()

@router.post("/{doc_id}/approve", response_model=DocumentOut)
async def approve_document(
    doc_id: int,
    current_user: User = Depends(check_role(["Approver"])),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.lawyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this document")

    doc.status = "Approved"
    db.commit()
    db.refresh(doc)
    
    # Notify CEO
    ceo_user = db.query(User).filter(User.role == "CEO").first()
    if ceo_user:
        send_email(
            ceo_user.email, 
            "Document Approved", 
            f"The document submitted on {doc.created_at} has been approved by {current_user.full_name}."
        )

    return doc

@router.post("/{doc_id}/reject", response_model=DocumentOut)
async def reject_document(
    doc_id: int,
    payload: DocumentUpdate,
    current_user: User = Depends(check_role(["Approver"])),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.lawyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this document")

    doc.status = "Rejected"
    doc.comments = payload.comments
    db.commit()
    db.refresh(doc)
    
    # Notify CEO
    ceo_user = db.query(User).filter(User.role == "CEO").first()
    if ceo_user:
        send_email(
            ceo_user.email, 
            "Document Rejected", 
            f"The document submitted on {doc.created_at} has been rejected by {current_user.full_name}.\n\nComments: {payload.comments}"
        )

    return doc
