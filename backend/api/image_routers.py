from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.image_translation_service import ImageTranslationService
from typing import Dict, Any
from backend.services.translation_service import translate_text
from backend.services.draw_service import DrawService

router = APIRouter()

# Initialize service with OpenRouter API key
image_service = ImageTranslationService(
    api_key="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"
)

# Cloudinary API key
CLOUDINARY_API_KEY = "g9AIU2wXL2JtYavmHKukq0SgNTg"

@router.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract text and positions from uploaded image
    Args:
        file: Uploaded image file
    Returns:
        Dict containing extracted text regions with positions
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed."
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Upload to Cloudinary and get URL
        image_url = image_service.upload_image_to_cloudinary(
            image_bytes=image_bytes,
            api_key=CLOUDINARY_API_KEY
        )
        
        # Extract text with positions
        text_regions = image_service.extract_sentences_with_positions(image_url)

        # Translate text
        for text_region in text_regions:
            text_region['text'] = translate_text(text_region['text'])

        draw_service = DrawService(font_path="arial.ttf", font_size=16)
        image_with_text = draw_service.draw_text_on_image(image_url, text_regions)
        new_image_url = image_service.upload_image_to_cloudinary(
            image_bytes=image_with_text,
            api_key=CLOUDINARY_API_KEY
        )

        return {
            "success": True,
            "image_url": new_image_url,
            "text_regions": text_regions,
            "new_image_url": new_image_url
        }
        
    except Exception as e:
        # Log the error (you might want to use proper logging)
        print(f"Error processing image: {str(e)}")
        
        # Return appropriate error response
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )