import asyncio
import json
import os
import sys

# Add backend to path so we can import from the 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import rag_service

async def bulk_ingest(file_path: str):
    """
    Reads a JSON file containing a list of laws and ingests them into the vector database.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # 1. Load the JSON data
    print(f"Loading data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            laws = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            return

    if not isinstance(laws, list):
        print("Error: JSON file must contain a list of law objects.")
        return

    print(f"Found {len(laws)} laws. Starting ingestion process...")

    # 2. Iterate through each law and ingest it sequentially to avoid API rate limits
    successful = 0
    failed = 0

    for index, law in enumerate(laws):
        law_text = law.get("law_text")
        metadata = law.get("metadata", {})
        article_id = metadata.get("article_id", f"unknown-id-{index}")

        if not law_text:
            print(f"[{index + 1}/{len(laws)}] Skipping record: Missing 'law_text'.")
            failed += 1
            continue

        try:
            print(f"[{index + 1}/{len(laws)}]  Ingesting: {article_id}...")
            # This calls the Gemini API to get the embedding and saves it to Pinecone
            await rag_service.ingest_law(law_text, metadata)
            print(f"  ✅ Successfully stored {article_id}")
            successful += 1
            
            # Optional: Add a small delay if you hit Gemini API rate limits (e.g., 15 Requests Per Minute on free tier)
            await asyncio.sleep(2) 
            
        except Exception as e:
            print(f" Failed to store {article_id}: {e}")
            failed += 1

    # 3. Print a final summary
    print("\n--- Ingestion Complete ---")
    print(f"Total processed: {len(laws)}")
    print(f"Successfully stored: {successful}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    # Provide the path to your JSON file here
    json_file_path = "data.json" 
    
    # Run the async bulk_ingest function
    asyncio.run(bulk_ingest(json_file_path))
