import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-pro")

def process_input(text):

    instruction = f"""
Process the following user input describing music.
Rewrite it clearly and descriptively.

INPUT:
{text}
"""

    response = model.generate_content(instruction)

    return response.text