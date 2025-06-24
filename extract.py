import fitz  # PyMuPDF
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        page_text = page.get_text()
        if page_text.strip():  # du texte est détecté => texte "vrai"
            text += page_text
        else:
            # sinon, OCR de l'image de la page
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img, lang='fra')  # ou 'eng' pour l'anglais
            text += ocr_text

    return text
