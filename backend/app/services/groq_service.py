import os
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
        """
        if not self.client:
            # If Groq isn't configured, we'll need to fall back or error out
            return {"evaluations": [], "error": "GROQ_API_KEY is not set."}
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        
        prompt = f"""
        You are an expert legal compliance AI. Evaluate the following list of Terms of Service clauses against the provided laws.
        
        Relevant Laws:
        {context_str}
        
        Clauses to Evaluate:
        {clauses_with_ids}
        
        For EACH clause, classify it as exactly one of: "violation", "warning", or "compliant".
        If it is a violation or warning, provide a brief reasoning and a "safe_alternative" that rewrites the clause to be fully compliant.
        
        Return the result as a valid JSON object with a key "evaluations" which is an array of objects.
        Each object in the array MUST have:
        - "id": integer (matching the ID provided above)
        - "status": string ("violation", "warning", or "compliant")
        - "reasoning": string (brief explanation)
        - "safe_alternative": string (rewritten text, or empty string if compliant)
        
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
            import json
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            return {"evaluations": [], "error": str(e)}

groq_service = GroqService()
