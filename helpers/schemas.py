from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    source_language: str = Field(..., example="eng_Latn")
    target_language: str = Field(..., example="kan_Knda")
    text: str = Field(..., min_length=1, example="Hello, how are you?")


class TranslationResponse(BaseModel):
    translated_text: str


class ImageTranslationRequest(BaseModel):
    image_b64: str = Field(..., description="Base64-encoded image")
    source_language: str = Field(..., example="kan_Knda")
    target_language: str = Field(..., example="eng_Latn")


class AudioTranslationRequest(BaseModel):
    audio_b64: str = Field(..., description="Base64-encoded audio file")
    source_language: str = Field(..., example="kan_Knda")
    target_language: str = Field(..., example="eng_Latn")


class AudioTranslationResponse(BaseModel):
    translated_text: str
    audio_b64: str = Field(..., description="Base64-encoded MP3 of synthesized speech")
