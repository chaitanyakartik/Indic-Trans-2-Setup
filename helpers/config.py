import os
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_CONFIG = {
    "en-indic": "ai4bharat/indictrans2-en-indic-1B",
    "indic-en": "ai4bharat/indictrans2-indic-en-1B",
    "indic-indic": "ai4bharat/indictrans2-indic-indic-1B",
}

API_KEY = "gok1-secret#*&%-key"

CHUNK_LIMIT = 600  # chars; empirically safe (model truncation seen at ~750-800 chars)

# OCR microservice (runs in surya_env on localhost)
OCR_SERVICE_URL = os.environ.get("OCR_SERVICE_URL", "http://127.0.0.1:8010")
OCR_TIMEOUT = int(os.environ.get("OCR_TIMEOUT", "120"))
# Google Cloud credentials for Speech-to-Text and Text-to-Speech
GOOGLE_CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "keys/gok-ipgrs-voice-sa.json",
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH
