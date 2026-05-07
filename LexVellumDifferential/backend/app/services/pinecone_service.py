from pinecone import Pinecone
from app.core.config import settings
class PineconeService:
    def __init__(self):
        self.index_name = settings.PINECONE_INDEX_NAME
        self.pc = None
        self.index = None
        if settings.PINECONE_API_KEY:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index = self.pc.Index(self.index_name)
    async def upsert_vectors(self, vectors: list[dict]):
        if not self.index:
            raise ValueError("Pinecone index is not initialized. Check API key.")
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)
    async def query_similar(self, query_vector: list[float], top_k: int = 3) -> list[dict]:
        if not self.index:
            raise ValueError("Pinecone index is not initialized. Check API key.")
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        return response['matches']
    async def query_similar_by_jurisdiction(self, query_vector: list[float], jurisdiction: str, top_k: int = 3) -> list[dict]:
        if not self.index:
            raise ValueError("Pinecone index is not initialized. Check API key.")
        if jurisdiction.upper() == "GDPR":
            metadata_filter = {
                "jurisdiction": {"$eq": "EU"},
            }
        elif jurisdiction.upper() == "USA":
            metadata_filter = {
                "$or": [
                    {"jurisdiction": {"$eq": "USA"}},
                    {"jurisdiction": {"$eq": "USA - California"}},
                    {"jurisdiction": {"$eq": "USA - Federal"}},
                ]
            }
        elif jurisdiction.upper() == "EU":
            metadata_filter = {
                "jurisdiction": {"$eq": "EU"},
            }
        else:
            metadata_filter = {
                "jurisdiction": {"$eq": jurisdiction},
            }
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=metadata_filter
        )
        return response['matches']
pinecone_service = PineconeService()
