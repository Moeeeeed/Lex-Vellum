from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/rag", tags=["RAG"])

class IngestRequest(BaseModel):
    law_text: str
    metadata: dict

class AnalyzeRequest(BaseModel):
    sentence: str

@router.post("/ingest")
async def ingest_law_endpoint(request: IngestRequest):
    """
    Ingests a raw legal text into the Pinecone Vector DB.
    """
    try:
        result = await rag_service.ingest_law(request.law_text, request.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_sentence_endpoint(request: AnalyzeRequest):
    """
    Analyzes a single ToS sentence against the vector DB laws.
    """
    try:
        result = await rag_service.analyze_tos_sentence(request.sentence)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
