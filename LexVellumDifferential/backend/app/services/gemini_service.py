import google.generativeai as genai
from app.core.config import settings

# Configure the Gemini API
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        # We use text-embedding-004 for generating embeddings
        self.embedding_model_name = 'models/text-embedding-004'
        # We use gemini-1.5-flash for fast text generation
        self.text_model_name = 'gemini-1.5-flash'
        
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
            task_type="retrieval_document"
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

gemini_service = GeminiService()
