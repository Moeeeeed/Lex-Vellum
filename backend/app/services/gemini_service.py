import google.generativeai as genai
from app.core.config import settings

# Configure the Gemini API
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        # We use gemini-embedding-2 for generating embeddings (1024 dimensions for Pinecone)
        self.embedding_model_name = 'models/gemini-embedding-2'
        # We use gemini-2.5-flash for fast text generation
        self.text_model_name = 'gemini-2.5-flash'
        
        self.text_model = genai.GenerativeModel(self.text_model_name)

    async def get_embedding(self, text: str) -> list[float]:
        """
        Generates an embedding vector for the given text.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot generate embeddings.")
            
        result = genai.embed_content(
            model=self.embedding_model_name,
            content=text,
            task_type="retrieval_document",
            output_dimensionality=1024
        )
        return result['embedding']

    async def generate_safe_alternative(self, violation_text: str, laws_context: list[str]) -> str:
        """
        Generates a safe alternative for a violating ToS sentence based on relevant laws.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot generate text.")
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        prompt = f"""
        You are an expert international lawyer AI.
        
        The following sentence from a Terms of Service draft violates these regional laws:
        
        Violating Sentence:
        "{violation_text}"
        
        Relevant Laws:
        {context_str}
        
        Please rewrite the sentence to be a "Safe Alternative" that complies with all the provided laws.
        Return ONLY the rewritten text, nothing else.
        """
        
        response = self.text_model.generate_content(prompt)
        return response.text.strip()

    async def evaluate_clause_compliance(self, clause_text: str, laws_context: list[str]) -> dict:
        """
        Evaluates a legal clause against a set of laws and returns a structured JSON response.
        Status can be: "violation", "warning", or "compliant".
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot evaluate compliance.")
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        prompt = f"""
        You are an expert legal compliance AI. Evaluate the following Terms of Service clause against the provided laws.
        Classify the clause as exactly one of: "violation", "warning", or "compliant".
        If it is a violation or warning, provide a brief reasoning and a "safe_alternative" that rewrites the clause to be fully compliant. If it is compliant, leave safe_alternative empty.
        
        Clause to Evaluate:
        "{clause_text}"
        
        Relevant Laws:
        {context_str}
        
        Return the result as a valid JSON object with the following keys:
        - "status": string ("violation", "warning", or "compliant")
        - "reasoning": string (brief explanation)
        - "safe_alternative": string (rewritten text, or empty string if compliant)
        """
        
        # We request structured JSON output using generation_config
        import asyncio
        from google.api_core.exceptions import ResourceExhausted
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.text_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                break
            except ResourceExhausted as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Gemini Rate Limit hit. Waiting 30 seconds before retrying... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(30)
                
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback in case the model failed to return valid JSON
            return {
                "status": "warning",
                "reasoning": "Failed to parse AI response as JSON.",
                "safe_alternative": clause_text
            }

    async def evaluate_document_batch(self, clauses: list[str], laws_context: list[str]) -> dict:
        """
        Evaluates a list of legal clauses in a single API call to minimize quota usage.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot evaluate compliance.")
            
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
        """
        
        import asyncio
        from google.api_core.exceptions import ResourceExhausted
        import json

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.text_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
            except ResourceExhausted as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Gemini Rate Limit hit. Waiting 45 seconds... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(45)
            except Exception as e:
                return {"evaluations": [], "error": str(e)}

gemini_service = GeminiService()
