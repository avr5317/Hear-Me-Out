from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(text):

    filename = "output.pdf"

    c = canvas.Canvas(filename, pagesize=letter)

    y = 750

    for line in text.split("\n"):
        c.drawString(100, y, line)
        y -= 20

    c.save()

    return filename