from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text: str
    src_lang: str = "en"
    tgt_lang: str = "vi"

class TranslationResponse(BaseModel):
    translated_text: str
