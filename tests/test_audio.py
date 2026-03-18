"""
Test the /translate-audio endpoint with a Kannada WAV file.
Usage: python tests/test_audio.py
"""
import base64
import sys
import time
import requests

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
AUDIO_PATH = "tests/test_data/Kathbath_0.wav"
OUTPUT_PATH = "tests/test_data/Kathbath_0_translated.mp3"


def main():
    r = requests.get(f"{BASE_URL}/health")
    if r.status_code != 200:
        print(f"Server not ready: {r.status_code} {r.text}")
        sys.exit(1)
    print(f"Server ready: {r.json()}")

    print(f"\nSending audio: {AUDIO_PATH}")
    with open(AUDIO_PATH, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("ascii")

    start = time.monotonic()
    resp = requests.post(
        f"{BASE_URL}/translate-audio",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "audio_b64": audio_b64,
            "source_language": "kan_Knda",
            "target_language": "eng_Latn",
        },
        timeout=120,
    )
    elapsed = time.monotonic() - start

    print(f"Status : {resp.status_code}  ({elapsed:.1f}s)")
    if resp.status_code == 200:
        body = resp.json()
        translated = body["translated_text"]
        print(f"Transcript length : {len(translated)} chars\n")
        print("--- Translation ---")
        print(translated)

        mp3_bytes = base64.b64decode(body["audio_b64"])
        with open(OUTPUT_PATH, "wb") as f:
            f.write(mp3_bytes)
        print(f"\nAudio saved to: {OUTPUT_PATH}  ({len(mp3_bytes)//1024}KB)")
    else:
        print("Error:", resp.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
