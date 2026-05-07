from google import genai
from google.genai import types
from app.core.config import settings
import json
import asyncio
class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.embedding_model_name = 'models/gemini-embedding-2' 
        self.text_model_name = 'models/gemini-3-flash-preview'
    async def get_embedding(self, text: str) -> list[float]:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot generate embeddings.")
        result = self.client.models.embed_content(
            model=self.embedding_model_name,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=1024)
        )
        return result.embeddings[0].values
    async def generate_safe_alternative(self, violation_text: str, laws_context: list[str]) -> str:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot generate text.")
        context_str = "\n".join([f"- {law}" for law in laws_context])
        prompt = f"""You are a senior legal compliance expert specializing in GDPR, CCPA, EU AI Act, and consumer protection law. Your task is to rewrite the following non-compliant clause into a fully compliant, legally sound alternative.

Applicable Legal Framework:
{context_str}

Non-Compliant Clause:
{violation_text}

Instructions:
- Write a comprehensive, legally precise alternative clause that fully resolves all violations.
- The rewritten clause must be specific, actionable, and enforceable.
- Use clear plain language while maintaining legal accuracy.
- Ensure the clause explicitly grants users their legal rights (right to erasure, data portability, consent withdrawal, etc.).
- The alternative must be at least 2-3 sentences long and address every legal concern.
- Do NOT use placeholders. Return only the final rewritten text."""
        response = self.client.models.generate_content(model=self.text_model_name, contents=prompt)
        return response.text.strip()
    async def evaluate_document_batch(self, clauses: list[str], laws_context: list[str]) -> dict:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot evaluate compliance.")
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        prompt = f"""You are a world-class legal compliance auditor with deep expertise in GDPR, CCPA, EU AI Act, ePrivacy Directive, and international consumer protection regulations.

Applicable Legal Framework (use ONLY these laws for evaluation):
{context_str}

Document Clauses to Evaluate:
{clauses_with_ids}

For each clause, perform a thorough analysis and output a JSON response. For every clause you MUST:
1. Determine the compliance status: 'violation' (clearly breaks a law), 'warning' (risky or ambiguous), or 'compliant' (fully compliant).
2. Identify ALL applicable law articles that are relevant.
3. Assign a compliance score from 0 (completely non-compliant) to 100 (fully compliant).
4. Provide a detailed reasoning of at least 2-3 sentences explaining WHY the clause is compliant, a warning, or a violation. Be specific about which legal article is implicated.
5. For violations: write a comprehensive safe_alternative of at least 3 sentences that fully resolves every legal concern and grants users their rights explicitly.

Output ONLY valid JSON in exactly this format:
{{"evaluations": [{{"id": <integer>, "status": "compliant"|"warning"|"violation", "flags": ["<Law Name> Article <X>: <Short Description>"], "score": <0-100>, "reasoning": "<Detailed 2-3 sentence explanation>", "safe_alternative": "<Full replacement text of 3+ sentences, empty string if compliant or warning>"}}]}}"""
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
    async def evaluate_document_against_jurisdiction(self, clauses: list[str], laws_context: list[str], jurisdiction: str) -> dict:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Cannot evaluate compliance.")
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        prompt = f"""You are a world-class legal compliance auditor specializing in {jurisdiction} law.

Applicable {jurisdiction} Legal Framework:
{context_str}

Document Clauses to Evaluate:
{clauses_with_ids}

Evaluate each clause STRICTLY against {jurisdiction} regulations only. For each clause you MUST:
1. Determine compliance status: 'violation', 'warning', or 'compliant'.
2. Cite the specific {jurisdiction} law article(s) implicated.
3. Assign a score from 0-100.
4. Write detailed reasoning of at least 2-3 sentences explaining the specific legal issue.
5. For violations: write a comprehensive 3+ sentence safe alternative that fully resolves the {jurisdiction}-specific violation.

Output ONLY valid JSON:
{{"evaluations": [{{"id": <integer>, "status": "compliant"|"warning"|"violation", "flags": ["<{jurisdiction} Law> Article <X>: <Short Description>"], "score": <0-100>, "reasoning": "<Detailed explanation>", "safe_alternative": "<Full replacement text, empty string if compliant or warning>"}}]}}"""
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
