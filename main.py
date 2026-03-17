import asyncio
import logging
import traceback

from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from helpers.config import API_KEY, DEVICE
from helpers.state import state
from helpers.model_loader import load_models
from helpers.schemas import TranslationRequest, TranslationResponse
from helpers.translation import translate_text
from helpers.pdf_utils import extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IndicTrans2 Translation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Semaphore: only 1 GPU call at a time — requests queue in asyncio, not on the GPU
_gpu_sem = asyncio.Semaphore(1)


@app.on_event("startup")
async def startup():
    await load_models(state)


# -----------------------
# Auth + readiness helpers
# -----------------------

def _check_auth(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

def _check_ready():
    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models are still loading, please wait")


# -----------------------
# Routes
# -----------------------

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest, x_api_key: str = Header(...)):
    _check_auth(x_api_key)
    _check_ready()
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")

    try:
        async with _gpu_sem:
            translated = await asyncio.to_thread(
                translate_text, request.text, request.source_language, request.target_language
            )
        return TranslationResponse(translated_text=translated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/translate-pdf", response_model=TranslationResponse)
async def translate_pdf(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
    x_api_key: str = Header(...),
):
    _check_auth(x_api_key)
    _check_ready()

    try:
        contents = await file.read()
        text = extract_text_from_pdf(contents)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        async with _gpu_sem:
            translated = await asyncio.to_thread(
                translate_text, text, source_language, target_language
            )
        return TranslationResponse(translated_text=translated)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"PDF translation error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/help")
def help():
    return {
        "endpoints": {
            "GET /health": {
                "description": "Check if server and models are ready",
                "auth": False,
                "response": {"status": "ok", "models_loaded": True, "device": "cuda"}
            },
            "POST /translate": {
                "description": "Translate text from one language to another",
                "auth": True,
                "body": {
                    "source_language": "e.g. eng_Latn",
                    "target_language": "e.g. hin_Deva",
                    "text": "Input text of any length — automatically chunked"
                },
                "response": {"translated_text": "..."}
            },
            "POST /translate-pdf": {
                "description": "Extract text from a PDF and translate it",
                "auth": True,
                "content_type": "multipart/form-data",
                "fields": {
                    "file": "PDF file",
                    "source_language": "e.g. eng_Latn",
                    "target_language": "e.g. hin_Deva"
                },
                "response": {"translated_text": "..."}
            },
            "GET /help": {
                "description": "This endpoint",
                "auth": False
            }
        },
        "auth": "Pass API key in header: X-API-Key: <key>",
        "language_codes": {
            "English": "eng_Latn",
            "Hindi": "hin_Deva",
            "Kannada": "kan_Knda",
            "Tamil": "tam_Taml",
            "Telugu": "tel_Telu",
            "Bengali": "ben_Beng",
            "Marathi": "mar_Deva",
            "Gujarati": "guj_Gujr",
            "Punjabi": "pan_Guru",
            "Malayalam": "mal_Mlym"
        }
    }


@app.get("/health")
def health_check():
    if state.models_loaded:
        return {"status": "ok", "models_loaded": True, "device": DEVICE}
    raise HTTPException(status_code=503, detail="Models still loading")


# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, log_level="info")
