from google import genai
from google.genai import types
from app.core.config import settings
import json
import asyncio

class GeminiService:
    def __init__(self):
        # Initialize the new Google GenAI client
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.embedding_model_name = 'models/gemini-embedding-2' # Standard Gemini embedding
        self.text_model_name = 'models/gemini-3-flash-preview'

    async def get_embedding(self, text: str) -> list[float]:
        """
        Generates an embedding vector for the given text.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot generate embeddings.")
            
        result = self.client.models.embed_content(
            model=self.embedding_model_name,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=1024)
        )
        return result.embeddings[0].values

    async def generate_safe_alternative(self, violation_text: str, laws_context: list[str]) -> str:
        """
        Generates a safe alternative for a violating ToS sentence.
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
        
        response = self.client.models.generate_content(model=self.text_model_name, contents=prompt)
        return response.text.strip()

    async def evaluate_document_batch(self, clauses: list[str], laws_context: list[str]) -> dict:
        """
        Evaluates a list of legal clauses in a single API call using JSON output.
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
        
        Return the result as a valid JSON object with a key "evaluations" which is an array of objects.
        Each object MUST have: id, status (violation/warning/compliant), score (0-100), 
        jurisdiction (array), reasoning, and safe_alternative (for violations).
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Request JSON output using config
                response = self.client.models.generate_content(
                    model=self.text_model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
            except Exception as e:
                # Catch the 429 Rate Limit error and wait 45 seconds
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit. Waiting 45 seconds before attempt {attempt + 2}...")
                    await asyncio.sleep(45)
                    continue
                return {"evaluations": [], "error": str(e)}

    async def evaluate_document_against_jurisdiction(self, clauses: list[str], laws_context: list[str], jurisdiction: str) -> dict:
        """
        Evaluates clauses specifically against a single jurisdiction's laws.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot evaluate compliance.")
            
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        
        prompt = f"""
        You are an expert legal compliance AI. Evaluate the following Terms of Service clauses SPECIFICALLY against {jurisdiction} laws only.
        
        {jurisdiction} Laws to check against:
        {context_str}
        
        Clauses to Evaluate:
        {clauses_with_ids}
        
        Return as a valid JSON object with key "evaluations" as array of objects.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.text_model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit. Waiting 45 seconds before attempt {attempt + 2}...")
                    await asyncio.sleep(45)
                    continue
                return {"evaluations": [], "error": str(e)}

gemini_service = GeminiService()