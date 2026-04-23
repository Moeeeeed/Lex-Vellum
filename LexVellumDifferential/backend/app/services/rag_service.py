from typing import List, Dict
from app.services.pinecone_service import pinecone_service
from app.services.gemini_service import gemini_service

class RagService:
    async def ingest_law(self, law_text: str, metadata: dict) -> dict:
        """
        Embeds a piece of legal text and stores it in Pinecone.
        """
        # 1. Generate embedding
        embedding = await gemini_service.get_embedding(law_text)
        
        # 2. Store in Pinecone
        vector_id = metadata.get('article_id', str(hash(law_text)))
        vector_record = {
            'id': vector_id,
            'values': embedding,
            'metadata': {**metadata, 'text': law_text}
        }
        
        await pinecone_service.upsert_vectors([vector_record])
        return {"status": "success", "vector_id": vector_id}

    async def analyze_tos_sentence(self, sentence: str) -> dict:
        """
        Takes a sentence from the ToS, finds relevant laws, and if a violation
        is found, generates a safe alternative.
        (For now, we just retrieve relevant laws to test the pipeline)
        """
        # 1. Embed the ToS sentence
        query_embedding = await gemini_service.get_embedding(sentence)
        
        # 2. Query Pinecone for similar laws
        matches = await pinecone_service.query_similar(query_embedding, top_k=3)
        
        # Extract the texts of the relevant laws
        relevant_laws = [match['metadata']['text'] for match in matches if 'text' in match['metadata']]
        
        # 3. Ask Gemini if it violates and generate a safe alternative
        # Note: In a full implementation we'd first check if there is an actual violation.
        # For phase 1, we will just pass it to the generator to see the RAG output.
        if not relevant_laws:
            return {"sentence": sentence, "status": "safe", "laws_checked": 0}
            
        safe_alternative = await gemini_service.generate_safe_alternative(sentence, relevant_laws)
        
        return {
            "original_sentence": sentence,
            "relevant_laws": relevant_laws,
            "safe_alternative": safe_alternative
        }

rag_service = RagService()
