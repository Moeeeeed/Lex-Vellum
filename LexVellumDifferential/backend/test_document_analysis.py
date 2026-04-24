import asyncio
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import rag_service

async def main():
    document_text = """
    Welcome to the LexVellum Enterprise Platform. 

To ensure global server reliability, your personal data will be automatically transferred and processed in various overseas data centers, including regions that may not maintain specialized data protection legislation, without requiring any further approval from you. 

Users who reside in California have the right to opt-out of the sale of their personal information. However, please note that users who exercise this right will be subject to a "Basic Tier" restriction, which includes slower platform speeds and an automatic $9.99 monthly maintenance fee. 

Finally, by checking the box to agree to these Terms of Service, you are also simultaneously giving your explicit consent to subscribe to our daily promotional marketing emails and authorizing us to share your browsing history with our third-party affiliate partners.
    """
    
    print("Analyzing document clause by clause...")
    result = await rag_service.analyze_full_document(document_text)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
