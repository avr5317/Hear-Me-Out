import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def process_input(text):

    instruction = f"""
Rewrite this music description clearly and descriptively.

INPUT:
{text}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=instruction
    )

    return response.text