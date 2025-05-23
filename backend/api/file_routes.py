from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.services.file_translate_service import extract_text_from_file, translate_text

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/file-translator/")
async def translate_uploaded_file(
    file: UploadFile = File(...),
    source_lang: str = Form("auto"),
    target_lang: str = Form("vi")
):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    try:
        print(f"Processing file: {file.filename}")
        print(f"Languages: {source_lang} -> {target_lang}")
        
        # Step 1: Extract text from file
        extracted_text = await extract_text_from_file(file)
        
        if not extracted_text or not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Cannot extract text from file")
        
        # Step 2: Translate extracted text
        translated_text = await translate_text(extracted_text, source_lang, target_lang)
        
        return {
            "success": True,
            "extracted_text": extracted_text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"File processing failed: {str(e)}")