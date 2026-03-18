"""
OCR microservice using Surya OCR.
Run with surya_env: source surya_env/bin/activate && python -m ocr.ocr_server
"""
import asyncio
import base64
import logging
from io import BytesIO

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Surya OCR Service")

_gpu_sem = asyncio.Semaphore(1)

# Module-level model state
_foundation: FoundationPredictor = None
_recognition: RecognitionPredictor = None
_detection: DetectionPredictor = None
_models_loaded = False


@app.on_event("startup")
async def startup():
    global _foundation, _recognition, _detection, _models_loaded
    logger.info("Loading Surya OCR models...")
    _foundation = FoundationPredictor()
    _recognition = RecognitionPredictor(_foundation)
    _detection = DetectionPredictor()
    _models_loaded = True
    logger.info("Surya OCR models loaded.")


class OCRRequest(BaseModel):
    images_b64: list[str]


class PageResult(BaseModel):
    text: str


class OCRResponse(BaseModel):
    pages: list[PageResult]


def _run_ocr(images: list[Image.Image]) -> list[str]:
    results = _recognition(images, det_predictor=_detection)
    return ["\n".join(line.text for line in page.text_lines) for page in results]


@app.post("/ocr", response_model=OCRResponse)
async def ocr(req: OCRRequest):
    if not _models_loaded:
        raise HTTPException(status_code=503, detail="Models still loading")
    if not req.images_b64:
        raise HTTPException(status_code=400, detail="No images provided")

    images = [Image.open(BytesIO(base64.b64decode(b64))) for b64 in req.images_b64]

    async with _gpu_sem:
        texts = await asyncio.to_thread(_run_ocr, images)

    return OCRResponse(pages=[PageResult(text=t) for t in texts])


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": _models_loaded}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
