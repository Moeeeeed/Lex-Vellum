import os
import json
from groq import AsyncGroq
from app.core.config import settings
class GroqService:
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    async def evaluate_document_batch(self, clauses: list[str], laws_context: list[str]) -> dict:
        if not self.client:
            return {"evaluations": [], "error": "GROQ_API_KEY is not set."}
        context_str = "\n".join([f"- {law}" for law in laws_context])
        clauses_with_ids = "\n".join([f"ID {i+1}: {clause}" for i, clause in enumerate(clauses)])
        prompt = f"""You are a world-class legal compliance auditor with deep expertise in GDPR, CCPA, EU AI Act, ePrivacy Directive, and international consumer protection regulations.

Applicable Legal Framework (use ONLY these laws for evaluation):
{context_str}

Document Clauses to Evaluate:
{clauses_with_ids}

For each clause, perform a thorough analysis. For every clause you MUST:
1. Determine the compliance status: 'violation' (clearly breaks a law), 'warning' (risky or ambiguous), or 'compliant' (fully compliant).
2. Identify ALL applicable law articles that are relevant.
3. Assign a compliance score from 0 (completely non-compliant) to 100 (fully compliant).
4. Provide a detailed reasoning of at least sentences explaining WHY the clause is compliant, a warning, or a violation. Be specific about which legal article is implicated.
5. For violations: write a comprehensive safe_alternative of at least 3 sentences that fully resolves every legal concern.

Output ONLY valid JSON:
{{"evaluations": [{{"id": <integer>, "status": "compliant"|"warning"|"violation", "flags": ["<Law Name> Article <X>: <Short Description>"], "score": <0-100>, "reasoning": "<Detailed 2-3 sentence explanation>", "safe_alternative": "<Full replacement text of 3+ sentences, empty string if compliant or warning>"}}]}}"""
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
        if not self.client:
            return {"evaluations": [], "error": "GROQ_API_KEY is not set."}
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
        if not self.client:
            return {"answer": "GROQ_API_KEY is not set.", "citations": []}
        context_str = "\n".join([f"- {law}" for law in laws_context])
        prompt = f"""You are a senior legal AI assistant with expertise in international compliance law. Answer the user's legal question thoroughly using only the law excerpts provided below.

Legal Knowledge Base:
{context_str}

User Question: {query}

Instructions:
- Provide a comprehensive, well-reasoned answer of at least 3-4 sentences.
- Cite specific law articles to support your answer.
- If the answer involves a legal risk, explain the consequences clearly.
- Output ONLY valid JSON: {{"answer": "<your detailed answer>", "citations": ["<relevant law excerpt 1>", "<relevant law excerpt 2>"] }}"""
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
