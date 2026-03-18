import base64
import logging

import fitz  # pymupdf
import httpx

from .config import OCR_SERVICE_URL, OCR_TEXT_THRESHOLD, OCR_TIMEOUT

logger = logging.getLogger(__name__)


def _needs_ocr(page: fitz.Page, text: str) -> bool:
    """True if the page has too little text but contains images (likely scanned)."""
    return len(text.strip()) < OCR_TEXT_THRESHOLD and bool(page.get_images(full=False))


def _render_page_b64(page: fitz.Page, dpi: int = 200) -> str:
    """Render a PDF page to a base64-encoded PNG."""
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat)
    return base64.b64encode(pix.tobytes("png")).decode("ascii")


async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF. Pages that appear scanned are OCR'd via the OCR service."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    page_texts = []
    ocr_indices = []
    ocr_images = []

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if _needs_ocr(page, text):
            logger.info(f"Page {i+1}: scanned, queuing for OCR")
            page_texts.append(None)
            ocr_indices.append(i)
            ocr_images.append(_render_page_b64(page))
        else:
            logger.info(f"Page {i+1}: text extracted ({len(text)} chars)")
            page_texts.append(text)

    if ocr_images:
        logger.info(f"Sending {len(ocr_images)} page(s) to OCR service")
        try:
            async with httpx.AsyncClient(timeout=OCR_TIMEOUT) as client:
                resp = await client.post(
                    f"{OCR_SERVICE_URL}/ocr",
                    json={"images_b64": ocr_images},
                )
                resp.raise_for_status()
        except httpx.ConnectError:
            raise RuntimeError(
                "OCR service is not reachable. Start it with: "
                "source surya_env/bin/activate && python -m ocr.ocr_server"
            )

        for idx, page_result in zip(ocr_indices, resp.json()["pages"]):
            ocr_text = page_result["text"]
            logger.info(f"Page {idx+1}: OCR returned {len(ocr_text)} chars")
            page_texts[idx] = ocr_text

    return "\n\n".join(t for t in page_texts if t).strip()
