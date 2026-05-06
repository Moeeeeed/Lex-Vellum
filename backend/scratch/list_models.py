from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

print("Available models:")
for model in client.models.list():
    print(f"Name: {model.name}, Supported Actions: {model.supported_actions}")
