from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.document import Document, DocumentCreate, DocumentOut, DocumentUpdate
from app.models.user import User
from app.api.auth_router import get_current_user, check_role
from app.services.email_service import send_email
from app.models.audit import AuditLog
from app.services.pdf_utils import render_template_to_pdf
router = APIRouter(prefix="/api/documents", tags=["documents"])
@router.post("/", response_model=DocumentOut)
async def submit_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["CEO", "Editor"]:
        raise HTTPException(status_code=403, detail="Only CEO or Editor can submit documents.")
    lawyer_id = payload.lawyer_id
    if not lawyer_id:
        all_approvers = db.query(User).filter(User.role == "Approver").all()
        if all_approvers:
            approver_loads = []
            for approver in all_approvers:
                pending_count = db.query(Document).filter(
                    Document.lawyer_id == approver.id,
                    Document.status == "Pending Review"
                ).count()
                approver_loads.append((pending_count, approver.id))
            approver_loads.sort(key=lambda x: x[0])
            lawyer_id = approver_loads[0][1]
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
    audit_archive = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        action="Document Version Archived (Initial Submission)",
        original_text="N/A",
        new_text=f"Initial text for Doc ID {new_doc.id}",
        full_document=new_doc.text,
        document_id=new_doc.id
    )
    db.add(audit_archive)
    db.commit()
    if lawyer_id:
        lawyer_user = db.query(User).filter(User.id == lawyer_id).first()
        if lawyer_user:
            email_body = f"Hello {lawyer_user.full_name},<br><br>A new document #{new_doc.id} has been submitted and is ready for your legal review.<br><br>Please log in to the dashboard to proceed."
            send_email(lawyer_user.email, "Action Required: Document Ready for Legal Review", email_body, is_html=True)
    return new_doc
@router.get("/", response_model=List[DocumentOut])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "CEO":
        return db.query(Document).order_by(Document.created_at.desc()).all()
    elif current_user.role == "Approver":
        return db.query(Document).order_by(Document.created_at.desc()).all()
    else:
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
    doc.status = "Approved"
    db.commit()
    db.refresh(doc)
    audit_archive = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        action="Document Version Archived (Final Approval)",
        original_text="Pending Review",
        new_text="Approved",
        full_document=doc.text,
        document_id=doc.id
    )
    db.add(audit_archive)
    db.commit()
    ceo_user = db.query(User).filter(User.role == "CEO").first()
    if ceo_user:
        tos_pdf = render_template_to_pdf("tos_pdf.html", {
            "doc_id": doc.id,
            "status": doc.status,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lawyer_name": current_user.full_name or "Assigned Lawyer",
            "text": doc.text
        })
        audit_trail = db.query(AuditLog).filter(AuditLog.document_id == doc.id).order_by(AuditLog.timestamp.asc()).all()
        audit_pdf = render_template_to_pdf("audit_pdf.html", {
            "doc_id": doc.id,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "audit_trail": audit_trail
        })
        email_body = f"<h2>Document #{doc.id} Approved</h2><p>The document has been <strong>approved</strong> by {current_user.full_name or current_user.email}.</p><p>Please find the Terms of Service PDF and Audit Trail attached.</p>"
        send_email(
            ceo_user.email, 
            f"URGENT: Document #{doc.id} Approved",
            email_body,
            is_html=True,
            attachments=[
                (f"ToS_Approved_{doc.id}.pdf", tos_pdf),
                (f"Audit_Trail_{doc.id}.pdf", audit_pdf)
            ]
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
    doc.status = "Rejected"
    doc.comments = payload.comments
    db.commit()
    db.refresh(doc)
    ceo_user = db.query(User).filter(User.role == "CEO").first()
    if ceo_user:
        tos_pdf = render_template_to_pdf("tos_pdf.html", {
            "doc_id": doc.id,
            "status": doc.status,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lawyer_name": current_user.full_name or "Assigned Lawyer",
            "text": doc.text
        })
        audit_trail = db.query(AuditLog).filter(AuditLog.document_id == doc.id).order_by(AuditLog.timestamp.asc()).all()
        audit_pdf = render_template_to_pdf("audit_pdf.html", {
            "doc_id": doc.id,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "audit_trail": audit_trail
        })
        email_body = f"<h2>Document #{doc.id} Rejected</h2><p>The document has been <strong>rejected</strong> by {current_user.full_name or current_user.email}.</p><p>Reason: {doc.comments}</p><p>Please find the Terms of Service PDF and Audit Trail attached.</p>"
        send_email(
            ceo_user.email, 
            f"ACTION REQUIRED: Document #{doc.id} Rejected",
            email_body,
            is_html=True,
            attachments=[
                (f"ToS_Rejected_{doc.id}.pdf", tos_pdf),
                (f"Audit_Trail_{doc.id}.pdf", audit_pdf)
            ]
        )
    return doc
@router.get("/{doc_id}/download/tos")
async def download_tos(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    lawyer = db.query(User).filter(User.id == doc.lawyer_id).first()
    lawyer_name = lawyer.full_name if lawyer else "N/A"
    pdf_bytes = render_template_to_pdf("tos_pdf.html", {
        "doc_id": doc.id,
        "status": doc.status,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "lawyer_name": lawyer_name,
        "text": doc.text
    })
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ToS_{doc_id}.pdf"}
    )
@router.get("/{doc_id}/download/audit")
async def download_audit(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    audit_trail = db.query(AuditLog).filter(AuditLog.document_id == doc.id).order_by(AuditLog.timestamp.asc()).all()
    pdf_bytes = render_template_to_pdf("audit_pdf.html", {
        "doc_id": doc.id,
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "audit_trail": audit_trail
    })
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Audit_Trail_{doc_id}.pdf"}
    )
