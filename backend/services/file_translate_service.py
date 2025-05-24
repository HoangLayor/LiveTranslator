import io
import asyncio
from fastapi import UploadFile
from typing import Optional
from backend.services.translation_service import translate_text as translate_func

# For PDF processing
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# For DOCX processing  
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# For image OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file based on file type"""
    
    file_content = await file.read()
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.pdf'):
            return await extract_from_pdf(file_content)
        elif filename.endswith('.docx'):
            return await extract_from_docx(file_content)
        elif filename.endswith(('.jpg', '.jpeg', '.png')):
            return await extract_from_image(file_content)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
            
    except Exception as e:
        raise Exception(f"Text extraction failed: {str(e)}")

async def extract_from_pdf(content: bytes) -> str:
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        raise Exception("PDF processing not available. Install PyMuPDF: pip install PyMuPDF")
    
    def _extract():
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _extract)
    return text.strip()

async def extract_from_docx(content: bytes) -> str:
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        raise Exception("DOCX processing not available. Install python-docx: pip install python-docx")
    
    def _extract():
        doc = Document(io.BytesIO(content))
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _extract)
    return text.strip()

async def extract_from_image(content: bytes) -> str:
    """Extract text from image using OCR"""
    if not OCR_AVAILABLE:
        raise Exception("OCR not available. Install: pip install pytesseract pillow")
    
    def _extract():
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image, lang='vie+eng')
        return text
    
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _extract)
    return text.strip()

# Translation function (integrate with existing translation service)
async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using existing translation service"""
    try:
        # Run translation in thread pool if it's blocking
        loop = asyncio.get_event_loop()
        translated = await loop.run_in_executor(
            None, 
            translate_func, 
            text, 
            source_lang, 
            target_lang
        )
        return str(translated)
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")