# # rest_routes.py - Placeholder file
# from fastapi import APIRouter
# from backend.models.translation_model import TranslationRequest, TranslationResponse
# from backend.services.translation_service import translate_with_api

# router = APIRouter()

# @router.post("/translate", response_model=TranslationResponse)
# def translate_text(request: TranslationRequest):
#     translated = translate_with_api(request.text, request.src_lang, request.tgt_lang)
#     return TranslationResponse(translated_text=translated)

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "OK"}