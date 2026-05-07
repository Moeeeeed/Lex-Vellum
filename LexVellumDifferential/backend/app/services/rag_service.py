from typing import List, Dict
from app.services.pinecone_service import pinecone_service
from app.services.gemini_service import gemini_service
from app.services.groq_service import groq_service
JURISDICTION_FLAG_MAP = {
    "EU": "🇪🇺",
    "GDPR": "🇪🇺",
    "USA": "🇺🇸",
    "UK": "🇬🇧",
    "Canada": "🇨🇦",
    "Australia": "🇦🇺",
}
class RagService:
    async def ingest_law(self, law_text: str, metadata: dict) -> dict:
        embedding = await gemini_service.get_embedding(law_text)
        vector_id = metadata.get('article_id', str(hash(law_text)))
        vector_record = {
            'id': vector_id,
            'values': embedding,
            'metadata': {**metadata, 'text': law_text}
        }
        await pinecone_service.upsert_vectors([vector_record])
        return {"status": "success", "vector_id": vector_id}
    def chunk_document(self, text: str) -> list[str]:
        import re
        chunks = [chunk.strip() for chunk in re.split(r'\n\s*\n', text)]
        return [chunk for chunk in chunks if len(chunk) > 30]
    def _compute_differential_scores(self, evaluated_clauses: list[dict]) -> dict:
        if not evaluated_clauses:
            return {
                "overall_score": 0,
                "jurisdiction_scores": {"EU": 0, "USA": 0, "GDPR": 0},
                "category_breakdown": {"violation": 0, "warning": 0, "compliant": 0}
            }
        all_scores = [c.get("score", 50) for c in evaluated_clauses]
        overall_score = round(sum(all_scores) / len(all_scores))
        jurisdiction_clause_scores: dict[str, list[int]] = {"EU": [], "USA": [], "GDPR": []}
        for clause in evaluated_clauses:
            score = clause.get("score", 50)
            jurisdictions = clause.get("jurisdiction", [])
            for j in jurisdictions:
                j_upper = j.upper()
                if j_upper in jurisdiction_clause_scores:
                    jurisdiction_clause_scores[j_upper].append(score)
        jurisdiction_scores = {}
        for j, scores in jurisdiction_clause_scores.items():
            if scores:
                jurisdiction_scores[j] = round(sum(scores) / len(scores))
            else:
                jurisdiction_scores[j] = overall_score
        category_breakdown = {"violation": 0, "warning": 0, "compliant": 0}
        for clause in evaluated_clauses:
            status = clause.get("status", "compliant")
            if status in category_breakdown:
                category_breakdown[status] += 1
        return {
            "overall_score": overall_score,
            "jurisdiction_scores": jurisdiction_scores,
            "category_breakdown": category_breakdown
        }
    def _enrich_clause_flags(self, clause: dict) -> dict:
        jurisdictions = clause.get("jurisdiction", [])
        flags = []
        for j in jurisdictions:
            flag = JURISDICTION_FLAG_MAP.get(j.upper(), "")
            if flag and flag not in flags:
                flags.append(flag)
        clause["flags"] = flags
        return clause
    async def analyze_full_document(self, document_text: str) -> dict:
        clauses = self.chunk_document(document_text)
        all_relevant_laws = set()
        clause_law_map = {}
        for i, clause in enumerate(clauses):
            query_embedding = await gemini_service.get_embedding(clause)
            matches = await pinecone_service.query_similar(query_embedding, top_k=2)
            laws = [match['metadata']['text'] for match in matches if 'text' in match['metadata']]
            all_relevant_laws.update(laws)
            clause_law_map[i + 1] = laws
        if groq_service.client:
            batch_result = await groq_service.evaluate_document_batch(clauses, list(all_relevant_laws))
        else:
            batch_result = await gemini_service.evaluate_document_batch(clauses, list(all_relevant_laws))
        evaluations_list = batch_result.get("evaluations", [])
        eval_lookup = {item['id']: item for item in evaluations_list}
        evaluated_clauses = []
        for i, clause in enumerate(clauses):
            clause_id = i + 1
            eval_data = eval_lookup.get(clause_id, {
                "status": "compliant",
                "score": 85,
                "jurisdiction": [],
                "reasoning": "No specific compliance issue detected.",
                "safe_alternative": ""
            })
            clause_obj = {
                "id": clause_id,
                "original_text": clause,
                "status": eval_data.get("status", "compliant"),
                "score": eval_data.get("score", 85),
                "jurisdiction": eval_data.get("jurisdiction", []),
                "reasoning": eval_data.get("reasoning", ""),
                "safe_alternative": eval_data.get("safe_alternative", ""),
                "relevant_laws": clause_law_map.get(clause_id, [])
            }
            clause_obj = self._enrich_clause_flags(clause_obj)
            evaluated_clauses.append(clause_obj)
        differential = self._compute_differential_scores(evaluated_clauses)
        return {
            "document_status": "analyzed",
            "total_clauses": len(clauses),
            "evaluated_clauses": evaluated_clauses,
            "overall_score": differential["overall_score"],
            "jurisdiction_scores": differential["jurisdiction_scores"],
            "category_breakdown": differential["category_breakdown"]
        }
    async def analyze_against_jurisdiction(self, document_text: str, jurisdiction: str) -> dict:
        clauses = self.chunk_document(document_text)
        all_relevant_laws = set()
        clause_law_map = {}
        for i, clause in enumerate(clauses):
            query_embedding = await gemini_service.get_embedding(clause)
            matches = await pinecone_service.query_similar_by_jurisdiction(
                query_embedding, jurisdiction=jurisdiction, top_k=3
            )
            laws = [match['metadata']['text'] for match in matches if 'text' in match['metadata']]
            all_relevant_laws.update(laws)
            clause_law_map[i + 1] = laws
        if not all_relevant_laws:
            for i, clause in enumerate(clauses):
                query_embedding = await gemini_service.get_embedding(clause)
                matches = await pinecone_service.query_similar(query_embedding, top_k=2)
                laws = [match['metadata']['text'] for match in matches if 'text' in match['metadata']]
                all_relevant_laws.update(laws)
        if groq_service.client:
            batch_result = await groq_service.evaluate_document_against_jurisdiction(
                clauses, list(all_relevant_laws), jurisdiction
            )
        else:
            batch_result = await gemini_service.evaluate_document_against_jurisdiction(
                clauses, list(all_relevant_laws), jurisdiction
            )
        evaluations_list = batch_result.get("evaluations", [])
        eval_lookup = {item['id']: item for item in evaluations_list}
        evaluated_clauses = []
        for i, clause in enumerate(clauses):
            clause_id = i + 1
            eval_data = eval_lookup.get(clause_id, {
                "status": "compliant",
                "score": 85,
                "jurisdiction": [jurisdiction],
                "reasoning": "No specific compliance issue detected.",
                "safe_alternative": ""
            })
            clause_obj = {
                "id": clause_id,
                "original_text": clause,
                "status": eval_data.get("status", "compliant"),
                "score": eval_data.get("score", 85),
                "jurisdiction": eval_data.get("jurisdiction", [jurisdiction]),
                "reasoning": eval_data.get("reasoning", ""),
                "safe_alternative": eval_data.get("safe_alternative", ""),
                "relevant_laws": clause_law_map.get(clause_id, [])
            }
            clause_obj = self._enrich_clause_flags(clause_obj)
            evaluated_clauses.append(clause_obj)
        differential = self._compute_differential_scores(evaluated_clauses)
        return {
            "document_status": "analyzed",
            "jurisdiction_checked": jurisdiction,
            "total_clauses": len(clauses),
            "evaluated_clauses": evaluated_clauses,
            "overall_score": differential["overall_score"],
            "jurisdiction_scores": differential["jurisdiction_scores"],
            "category_breakdown": differential["category_breakdown"]
        }
    async def legal_chat(self, query: str) -> dict:
        query_embedding = await gemini_service.get_embedding(query)
        matches = await pinecone_service.query_similar(query_embedding, top_k=5)
        laws_context = [m['metadata']['text'] for m in matches if 'text' in m['metadata']]
        result = await groq_service.chat(query, laws_context)
        result["raw_sources"] = laws_context
        return result
rag_service = RagService()
