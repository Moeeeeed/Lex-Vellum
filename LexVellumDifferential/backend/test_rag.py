import asyncio
import os
import sys

# add backend to path to allow absolute imports like `app.something`
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import rag_service

async def main():
    data = {
        "law_text": "GDPR Article 17 (Right to Erasure): The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay. The controller shall have the obligation to erase personal data without undue delay where one of the following grounds applies: the personal data are no longer necessary in relation to the purposes for which they were collected; or the data subject withdraws consent on which the processing is based. A company cannot retain user data indefinitely simply for future, undefined commercial use.",
        "metadata": {
            "jurisdiction": "EU",
            "article_id": "gdpr-art-17-erasure"
        }
    }
    
    print("Ingesting data...")
    result = await rag_service.ingest_law(data["law_text"], data["metadata"])
    print("Ingest result:", result)
    
    test_sentence = "We reserve the right to retain your data indefinitely for future commercial use."
    print(f"Testing RAG with sentence: '{test_sentence}'")
    analysis_result = await rag_service.analyze_tos_sentence(test_sentence)
    import json
    print("Analysis result:")
    print(json.dumps(analysis_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
