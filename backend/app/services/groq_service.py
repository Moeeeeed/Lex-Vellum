import os
import json
from groq import AsyncGroq
from app.core.config import settings

class GroqService:
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        # We use Llama 3.3 70B - fast and very capable for legal analysis
        self.model = "llama-3.3-70b-versatile"

    async def evaluate_document_batch(self, clauses: list[str], laws_context: list[str]) -> dict:
        """
        Evaluates a list of legal clauses using Groq Llama 3 for high-speed, high-quota analysis.
        Returns per-clause: status, score (0-100), jurisdiction, reasoning, safe_alternative.
        """
        if not self.client:
            return {"evaluations": [], "error": "GROQ_API_KEY is not set."}
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        
        prompt = f"""
        You are an expert legal compliance AI. Evaluate the following list of Terms of Service clauses against the provided laws.
        
        Relevant Laws:
        {context_str}
        
        Clauses to Evaluate:
        {clauses_with_ids}
        
        For EACH clause, you must:
        1. Classify it as exactly one of: "violation", "warning", or "compliant".
        2. Assign a compliance score from 0 to 100 (0 = severe violation, 100 = fully compliant).
        3. Identify which jurisdiction(s) the clause relates to. Use these codes: "EU", "USA", "GDPR". A clause can relate to multiple jurisdictions.
        4. If it is a "violation", provide a brief reasoning AND a "safe_alternative" that rewrites the clause to be fully compliant.
        5. If it is a "warning", provide a brief reasoning explaining why this could potentially be violated in the future, but set "safe_alternative" to an empty string.
        6. If it is "compliant", provide a brief reasoning and set "safe_alternative" to an empty string.
        
        Return the result as a valid JSON object with a key "evaluations" which is an array of objects.
        Each object in the array MUST have:
        - "id": integer (matching the ID provided above)
        - "status": string ("violation", "warning", or "compliant")
        - "score": integer (0 to 100)
        - "jurisdiction": array of strings (e.g. ["EU", "GDPR"] or ["USA"])
        - "reasoning": string (brief explanation)
        - "safe_alternative": string (rewritten text for violations ONLY, empty string otherwise)
        
        IMPORTANT: Return ONLY the JSON object. Do not include any conversational filler.
        """
        
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized legal compliance AI that outputs only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            return {"evaluations": [], "error": str(e)}

    async def evaluate_document_against_jurisdiction(self, clauses: list[str], laws_context: list[str], jurisdiction: str) -> dict:
        """
        Evaluates clauses specifically against a single jurisdiction's laws.
        Used for the individual EU/USA/GDPR check buttons.
        """
        if not self.client:
            return {"evaluations": [], "error": "GROQ_API_KEY is not set."}
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        
        prompt = f"""
        You are an expert legal compliance AI. Evaluate the following Terms of Service clauses SPECIFICALLY against {jurisdiction} laws only.
        
        {jurisdiction} Laws to check against:
        {context_str}
        
        Clauses to Evaluate:
        {clauses_with_ids}
        
        For EACH clause:
        1. Classify as "violation", "warning", or "compliant" based ONLY on {jurisdiction} laws.
        2. Assign a compliance score from 0 to 100.
        3. Set jurisdiction to ["{jurisdiction}"].
        4. For "violation": provide reasoning AND a safe_alternative rewrite.
        5. For "warning": provide reasoning, safe_alternative must be empty string.
        6. For "compliant": provide reasoning, safe_alternative must be empty string.
        
        Return as a valid JSON object:
        {{
          "evaluations": [
            {{
              "id": integer,
              "status": "violation" | "warning" | "compliant",
              "score": integer (0-100),
              "jurisdiction": ["{jurisdiction}"],
              "reasoning": string,
              "safe_alternative": string
            }}
          ]
        }}
        
        IMPORTANT: Return ONLY the JSON object.
        """
        
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized legal compliance AI that outputs only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            return {"evaluations": [], "error": str(e)}

    async def chat(self, query: str, laws_context: list[str]) -> dict:
        """
        Answers a legal question based on provided law context using Groq.
        """
        if not self.client:
            return {"answer": "GROQ_API_KEY is not set.", "citations": []}
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        
        prompt = f"""
        You are 'LexVellum AI', a specialized legal compliance assistant. 
        Answer the following user question using ONLY the provided verified legal context.
        
        Verified Legal Context:
        {context_str}
        
        User Question:
        {query}
        
        Instructions:
        1. Answer the question clearly and accurately based on the provided context.
        2. If the context does not contain the answer, say "I don't have enough verified information to answer this specifically, but based on general legal principles..." and provide a helpful but cautious response.
        3. Provide specific citations from the text if available (e.g. "According to Article 17...").
        4. Keep the tone professional, objective, and authoritative.
        
        Return the result as a JSON object:
        {{
          "answer": "Your detailed answer here...",
          "citations": ["Citation 1", "Citation 2"]
        }}
        """
        
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a legal AI assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            return {"answer": f"Error communicating with AI: {str(e)}", "citations": []}

groq_service = GroqService()
