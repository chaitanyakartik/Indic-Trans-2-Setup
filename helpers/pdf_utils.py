import base64
import logging

import fitz  # pymupdf
import httpx

from .config import OCR_SERVICE_URL, OCR_TIMEOUT

logger = logging.getLogger(__name__)

RENDER_DPI = 300


def _render_page_b64(page: fitz.Page) -> str:
    """Render a PDF page to a base64-encoded PNG at RENDER_DPI."""
    mat = fitz.Matrix(RENDER_DPI / 72.0, RENDER_DPI / 72.0)
    pix = page.get_pixmap(matrix=mat)
    return base64.b64encode(pix.tobytes("png")).decode("ascii")


async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Render every PDF page to a high-DPI PNG and OCR all pages via the OCR service."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    images_b64 = [_render_page_b64(page) for page in doc]
    logger.info(f"Rendered {len(images_b64)} page(s) at {RENDER_DPI} DPI, sending to OCR")

    try:
        async with httpx.AsyncClient(timeout=OCR_TIMEOUT) as client:
            resp = await client.post(
                f"{OCR_SERVICE_URL}/ocr",
                json={"images_b64": images_b64},
            )
            resp.raise_for_status()
    except httpx.ConnectError:
        raise RuntimeError(
            "OCR service is not reachable. Start it with: "
            "source surya_env/bin/activate && python -m ocr.ocr_server"
        )

    page_texts = [p["text"] for p in resp.json()["pages"]]
    for i, text in enumerate(page_texts):
        logger.info(f"Page {i+1}: OCR returned {len(text)} chars")

    return "\n\n".join(t for t in page_texts if t).strip()
