"""
Test the /translate-pdf endpoint with a scanned PDF.
Usage: python tests/test_scanned_pdf.py
"""
import sys
import time
import requests

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
PDF_PATH = "/home/chaitanya/translation-model/Indic-Trans-2-Setup/test_kannada_scanned.pdf"

def main():
    # Health check
    r = requests.get(f"{BASE_URL}/health")
    if r.status_code != 200:
        print(f"Server not ready: {r.status_code} {r.text}")
        sys.exit(1)
    print(f"Server ready: {r.json()}")

    print(f"\nSending scanned PDF: {PDF_PATH}")
    start = time.monotonic()

    with open(PDF_PATH, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/translate-pdf",
            headers={"X-API-Key": API_KEY},
            files={"file": ("test_kannada_scanned.pdf", f, "application/pdf")},
            data={
                "source_language": "kan_Knda",
                "target_language": "eng_Latn",
            },
            timeout=300,
        )

    elapsed = time.monotonic() - start

    print(f"Status : {resp.status_code}  ({elapsed:.1f}s)")
    if resp.status_code == 200:
        translated = resp.json()["translated_text"]
        print(f"Length : {len(translated)} chars\n")
        print("--- Translation ---")
        print(translated)
    else:
        print("Error:", resp.text)
        sys.exit(1)

if __name__ == "__main__":
    main()
