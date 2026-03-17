import io
import fitz
import requests

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
HEADERS = {"X-API-Key": API_KEY}


def _make_pdf(text: str) -> bytes:
    """Create a minimal in-memory PDF with the given text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), text, fontsize=12)
    return doc.tobytes()


def test_translate_pdf_single_page():
    pdf_bytes = _make_pdf("The sun rises in the east and sets in the west.")
    r = requests.post(
        f"{BASE_URL}/translate-pdf",
        headers=HEADERS,
        files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        data={"source_language": "eng_Latn", "target_language": "hin_Deva"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "translated_text" in body
    assert len(body["translated_text"]) > 0


def test_translate_pdf_multi_page():
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50, 100), f"Page {i+1}: The sky is blue and the grass is green.", fontsize=12)
    pdf_bytes = doc.tobytes()

    r = requests.post(
        f"{BASE_URL}/translate-pdf",
        headers=HEADERS,
        files={"file": ("multi.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        data={"source_language": "eng_Latn", "target_language": "hin_Deva"},
    )
    assert r.status_code == 200
    assert "translated_text" in r.json()


def test_translate_pdf_wrong_api_key():
    pdf_bytes = _make_pdf("Hello world.")
    r = requests.post(
        f"{BASE_URL}/translate-pdf",
        headers={"X-API-Key": "wrong-key"},
        files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        data={"source_language": "eng_Latn", "target_language": "hin_Deva"},
    )
    assert r.status_code == 403
