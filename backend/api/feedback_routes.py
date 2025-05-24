from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models.feedback_model import Feedback

router = APIRouter()

class FeedbackCreate(BaseModel):
    rating: int
    feedback_text: Optional[str] = None
    file_name: Optional[str] = None
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None

@router.post("/submit-feedback")
async def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    print("Received feedback:", feedback)
    try:
        # Validate rating
        if not 1 <= feedback.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        # Create new feedback entry
        db_feedback = Feedback(
            rating=feedback.rating,
            feedback_text=feedback.feedback_text,
            file_name=feedback.file_name,
            source_lang=feedback.source_lang,
            target_lang=feedback.target_lang,
            original_text=feedback.original_text,
            translated_text=feedback.translated_text
        )

        # Save to database
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": db_feedback.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 