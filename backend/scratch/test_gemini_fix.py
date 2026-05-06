import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import gemini_service

async def test_gemini():
    load_dotenv()
    print("Testing Gemini Embedding...")
    try:
        embedding = await gemini_service.get_embedding("This is a test document for legal compliance.")
        print(f"Success! Embedding length: {len(embedding)}")
    except Exception as e:
        print(f"Embedding failed: {e}")

    print("\nTesting Gemini Text Generation...")
    try:
        alternative = await gemini_service.generate_safe_alternative(
            "The user must give up all their rights forever.",
            ["EU Consumer Law", "GDPR"]
        )
        print(f"Success! Alternative: {alternative}")
    except Exception as e:
        print(f"Text generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
