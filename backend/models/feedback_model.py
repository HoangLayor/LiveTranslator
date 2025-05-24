from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    feedback_text = Column(Text)
    file_name = Column(String(255))
    source_lang = Column(String(10))
    target_lang = Column(String(10))
    original_text = Column(Text)
    translated_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 