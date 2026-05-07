from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.services.pdf_utils import extract_text_from_pdf
router = APIRouter(prefix="/api/rag", tags=["RAG"])
class IngestRequest(BaseModel):
    law_text: str
    metadata: dict
class AnalyzeRequest(BaseModel):
    sentence: str
class AnalyzeDocumentRequest(BaseModel):
    document_text: str
class AnalyzeJurisdictionRequest(BaseModel):
    document_text: str
    jurisdiction: str  
class ChatRequest(BaseModel):
    message: str
@router.post("/ingest")
async def ingest_law_endpoint(request: IngestRequest):
    try:
        result = await rag_service.ingest_law(request.law_text, request.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/analyze_document")
async def analyze_document_endpoint(request: AnalyzeDocumentRequest):
    try:
        result = await rag_service.analyze_full_document(request.document_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/upload_pdf")
async def upload_pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    try:
        file_bytes = await file.read()
        document_text = extract_text_from_pdf(file_bytes)
        if not document_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from the PDF. The file may be scanned or image-only."
            )
        result = await rag_service.analyze_full_document(document_text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/analyze_jurisdiction")
async def analyze_jurisdiction_endpoint(request: AnalyzeJurisdictionRequest):
    valid_jurisdictions = {"EU", "USA", "GDPR"}
    if request.jurisdiction.upper() not in valid_jurisdictions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid jurisdiction. Must be one of: {', '.join(valid_jurisdictions)}"
        )
    try:
        result = await rag_service.analyze_against_jurisdiction(
            request.document_text, request.jurisdiction.upper()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/chat")
async def chat_with_lexvellum_endpoint(request: ChatRequest):
    try:
        result = await rag_service.legal_chat(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
