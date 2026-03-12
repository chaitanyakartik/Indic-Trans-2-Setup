import os
import torch
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------
# Configuration
# -----------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_CONFIG = {
    "en-indic": "ai4bharat/indictrans2-en-indic-1B",
    "indic-en": "ai4bharat/indictrans2-indic-en-1B",
    "indic-indic": "ai4bharat/indictrans2-indic-indic-1B"
}

# -----------------------
# Global state
# -----------------------
class AppState:
    def __init__(self):
        self.models = {}
        self.models_loaded = False
        self.ip = None

state = AppState()

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(title="IndicTrans2 Translation API")

# -----------------------
# Load models at startup
# -----------------------
@app.on_event("startup")
async def load_models():
    logger.info("=" * 60)
    logger.info("Starting model loading...")
    logger.info(f"Device: {DEVICE}")
    logger.info("=" * 60)
    
    try:
        # Load IndicProcessor
        logger.info("[1/4] Loading IndicProcessor...")
        state.ip = IndicProcessor(inference=True)
        logger.info("✓ IndicProcessor loaded")
        
        # Load all three models
        for idx, (key, model_name) in enumerate(MODEL_CONFIG.items(), start=2):
            logger.info(f"[{idx}/4] Loading {key} model...")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            logger.info(f"  ✓ Tokenizer loaded")
            
            # Load model
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
            ).to(DEVICE)
            model.eval()
            logger.info(f"  ✓ Model loaded and moved to {DEVICE}")
            
            state.models[key] = {
                "tokenizer": tokenizer,
                "model": model
            }
        
        state.models_loaded = True
        logger.info("=" * 60)
        logger.info("✓ ALL MODELS LOADED SUCCESSFULLY!")
        logger.info(f"✓ models_loaded = {state.models_loaded}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Error loading models: {e}")
        import traceback
        traceback.print_exc()
        state.models_loaded = False

# -----------------------
# Helper function
# -----------------------
def get_model_key(src_lang: str, tgt_lang: str) -> str:
    """Determine which model to use based on language pair"""
    if src_lang == "eng_Latn" and tgt_lang != "eng_Latn":
        return "en-indic"
    elif src_lang != "eng_Latn" and tgt_lang == "eng_Latn":
        return "indic-en"
    elif src_lang != "eng_Latn" and tgt_lang != "eng_Latn":
        return "indic-indic"
    else:
        raise ValueError("eng_Latn to eng_Latn translation not supported")

# -----------------------
# Request / Response models
# -----------------------
class TranslationRequest(BaseModel):
    source_language: str = Field(..., example="eng_Latn")
    target_language: str = Field(..., example="kan_Knda")
    text: str = Field(..., min_length=1, example="Hello, how are you?")

class TranslationResponse(BaseModel):
    translated_text: str

# -----------------------
# Translation function
# -----------------------
def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """Simple translation function"""
    if not state.models_loaded or state.ip is None:
        raise RuntimeError("Models not loaded yet")
    
    # Preprocess
    batch = state.ip.preprocess_batch(
        [text],
        src_lang=src_lang,
        tgt_lang=tgt_lang
    )
    
    # Get the right model
    model_key = get_model_key(src_lang, tgt_lang)
    bundle = state.models[model_key]
    
    # Tokenize
    inputs = bundle["tokenizer"](
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
        return_attention_mask=True
    ).to(DEVICE)
    
    # Generate translation
    with torch.no_grad():
        tokens = bundle["model"].generate(
            **inputs,
            max_length=256,
            num_beams=5
        )
    
    # Decode
    decoded = bundle["tokenizer"].batch_decode(
        tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    
    # Postprocess
    translations = state.ip.postprocess_batch(decoded, lang=tgt_lang)
    
    return translations[0]

# -----------------------
# API endpoints
# -----------------------
@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest, x_api_key: str = Header(...)):
    """Translate text from source language to target language"""
    api_key = os.environ.get("TRANSLATION_API_KEY")
    if not api_key or x_api_key != api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

    logger.info(f"Translation request - models_loaded: {state.models_loaded}")
    
    if not state.models_loaded:
        raise HTTPException(
            status_code=503, 
            detail="Models are still loading, please wait"
        )
    
    if not request.text.strip():
        raise HTTPException(
            status_code=400, 
            detail="Input text cannot be empty"
        )
    
    try:
        translated_text = translate_text(
            request.text,
            request.source_language,
            request.target_language
        )
        return TranslationResponse(translated_text=translated_text)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.get("/health")
def health_check():
    """Check if the server and models are ready"""
    logger.info(f"Health check - models_loaded: {state.models_loaded}")
    
    if state.models_loaded:
        return {
            "status": "ok", 
            "models_loaded": True,
            "device": DEVICE
        }
    else:
        raise HTTPException(
            status_code=503, 
            detail="Models still loading"
        )

# -----------------------
# Main entry point
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
