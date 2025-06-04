from fastapi import APIRouter, UploadFile, File
from backend.services.image_translation_service import ImageTranslationService

router = APIRouter()
image_service = ImageTranslationService(
    api_key="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"
)
IMGBB_API_KEY = "785e57ea3a903daeaa39a49f3cc8bf38"


@router.post("/test-ocr")
async def test_ocr(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image_url = image_service.upload_image_to_imgbb(image_bytes, IMGBB_API_KEY)
        sentences = image_service.extract_sentences_with_positions(image_url)
        return {"success": True, "sentences": sentences}
    except Exception as e:
        return {"success": False, "error": str(e)}
