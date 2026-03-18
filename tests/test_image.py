"""
Test the /translate-image endpoint with a Kannada image.
Usage: python tests/test_image.py
"""
import base64
import sys
import time
import requests

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
IMAGE_PATH = "tests/test_data/test_image_kn_2.png"


def main():
    r = requests.get(f"{BASE_URL}/health")
    if r.status_code != 200:
        print(f"Server not ready: {r.status_code} {r.text}")
        sys.exit(1)
    print(f"Server ready: {r.json()}")

    print(f"\nSending image: {IMAGE_PATH}")
    with open(IMAGE_PATH, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("ascii")

    start = time.monotonic()
    resp = requests.post(
        f"{BASE_URL}/translate-image",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "image_b64": image_b64,
            "source_language": "kan_Knda",
            "target_language": "eng_Latn",
        },
        timeout=120,
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
