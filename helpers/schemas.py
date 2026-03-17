from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    source_language: str = Field(..., example="eng_Latn")
    target_language: str = Field(..., example="kan_Knda")
    text: str = Field(..., min_length=1, example="Hello, how are you?")


class TranslationResponse(BaseModel):
    translated_text: str
