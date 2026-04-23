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

pinecone_service = PineconeService()
