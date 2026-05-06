from pinecone import Pinecone
from app.core.config import settings

class PineconeService:
    def __init__(self):
        self.index_name = settings.PINECONE_INDEX_NAME
        self.pc = None
        self.index = None
        
        # Initialize Pinecone if API key is present
        if settings.PINECONE_API_KEY:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index = self.pc.Index(self.index_name)

    async def upsert_vectors(self, vectors: list[dict]):
        """
        Upserts vectors into the Pinecone index.
        vectors should be a list of dictionaries: 
        [{'id': str, 'values': list[float], 'metadata': dict}]
        """
        if not self.index:
            raise ValueError("Pinecone index is not initialized. Check API key.")
            
        # Pinecone accepts upserts in batches, we'll do up to 100 at a time
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)

    async def query_similar(self, query_vector: list[float], top_k: int = 3) -> list[dict]:
        """
        Queries the Pinecone index for the most similar vectors.
        Returns the top_k matches including their metadata.
        """
        if not self.index:
            raise ValueError("Pinecone index is not initialized. Check API key.")
            
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        return response['matches']

    async def query_similar_by_jurisdiction(self, query_vector: list[float], jurisdiction: str, top_k: int = 3) -> list[dict]:
        """
        Queries the Pinecone index for similar vectors filtered by jurisdiction.
        jurisdiction can be: 'EU', 'USA', 'USA - California', 'GDPR' (mapped to EU with gdpr- prefix filter)
        """
        if not self.index:
            raise ValueError("Pinecone index is not initialized. Check API key.")

        # Build the metadata filter based on jurisdiction
        if jurisdiction.upper() == "GDPR":
            # GDPR articles are stored under jurisdiction "EU" with article_id starting with "gdpr-"
            metadata_filter = {
                "jurisdiction": {"$eq": "EU"},
            }
        elif jurisdiction.upper() == "USA":
            # USA laws include California (CCPA) and federal laws
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
