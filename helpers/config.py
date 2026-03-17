import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_CONFIG = {
    "en-indic": "ai4bharat/indictrans2-en-indic-1B",
    "indic-en": "ai4bharat/indictrans2-indic-en-1B",
    "indic-indic": "ai4bharat/indictrans2-indic-indic-1B",
}

API_KEY = "gok1-secret#*&%-key"

CHUNK_LIMIT = 600  # chars; empirically safe (model truncation seen at ~750-800 chars)
