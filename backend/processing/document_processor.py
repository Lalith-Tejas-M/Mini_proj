import fitz  # PyMuPDF
from docx import Document
import io
from utils.text_utils import clean_and_normalize

async def process_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    # Open from memory
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")
    
    return clean_and_normalize(text)

async def process_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        raise ValueError(f"Error parsing DOCX: {str(e)}")
        
    return clean_and_normalize(text)

async def process_document(file_bytes: bytes, filename: str) -> str:
    """Route document to appropriate parser based on extension."""
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return await process_pdf(file_bytes)
    elif filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
        return await process_docx(file_bytes)
    elif filename_lower.endswith('.txt'):
        return clean_and_normalize(file_bytes.decode('utf-8', errors='replace'))
    else:
        raise ValueError("Unsupported document format. Please upload PDF, DOCX, or TXT.")
