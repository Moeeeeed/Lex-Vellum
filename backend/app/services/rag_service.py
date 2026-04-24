from typing import List, Dict
from app.services.pinecone_service import pinecone_service
from app.services.gemini_service import gemini_service
from app.services.groq_service import groq_service

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

    def chunk_document(self, text: str) -> list[str]:
        """
        Splits a document into logical clauses (paragraphs).
        """
        import re
        # Split by double newline to get paragraphs, filter out empty ones
        chunks = [chunk.strip() for chunk in re.split(r'\n\s*\n', text)]
        return [chunk for chunk in chunks if chunk]

    async def analyze_full_document(self, document_text: str) -> dict:
        """
        Analyzes a full document in a single batch to minimize API quota usage.
        """
        clauses = self.chunk_document(document_text)
        
        # 1. Collect all relevant laws for all clauses first (High quota embedding/vector search)
        all_relevant_laws = set()
        clause_law_map = {} # To keep track which laws belong to which clause for context
        
        for i, clause in enumerate(clauses):
            query_embedding = await gemini_service.get_embedding(clause)
            matches = await pinecone_service.query_similar(query_embedding, top_k=2)
            laws = [match['metadata']['text'] for match in matches if 'text' in match['metadata']]
            all_relevant_laws.update(laws)
            clause_law_map[i+1] = laws

        # 2. Call the AI (Groq is preferred for its high speed and quota)
        if groq_service.client:
            batch_result = await groq_service.evaluate_document_batch(clauses, list(all_relevant_laws))
        else:
            # Fallback to Gemini if Groq is not configured
            batch_result = await gemini_service.evaluate_document_batch(clauses, list(all_relevant_laws))
            
        evaluations_list = batch_result.get("evaluations", [])
        
        # 3. Map results back to structured format
        evaluated_clauses = []
        # Create a lookup for evaluations by ID
        eval_lookup = {item['id']: item for item in evaluations_list}
        
        for i, clause in enumerate(clauses):
            clause_id = i + 1
            eval_data = eval_lookup.get(clause_id, {
                "status": "compliant", 
                "reasoning": "Batch evaluation did not return data for this clause.",
                "safe_alternative": ""
            })
            
            evaluated_clauses.append({
                "id": clause_id,
                "original_text": clause,
                "status": eval_data.get("status", "compliant"),
                "reasoning": eval_data.get("reasoning", ""),
                "safe_alternative": eval_data.get("safe_alternative", ""),
                "relevant_laws": clause_law_map.get(clause_id, [])
            })
            
        return {
            "document_status": "analyzed",
            "total_clauses": len(clauses),
            "evaluated_clauses": evaluated_clauses
        }

rag_service = RagService()
