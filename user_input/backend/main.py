from fastapi import FastAPI
from gemini_processor import process_input
from pdf_generator import create_pdf

app = FastAPI()

@app.post("/process")

def process(data: dict):

    user_text = data["text"]

    processed_text = process_input(user_text)

    pdf_file = create_pdf(processed_text)

    return {
        "pdf": pdf_file,
        "text": processed_text
    }