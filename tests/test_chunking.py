import requests

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def translate(text):
    r = requests.post(
        f"{BASE_URL}/translate",
        headers=HEADERS,
        json={"source_language": "eng_Latn", "target_language": "hin_Deva", "text": text},
    )
    assert r.status_code == 200, f"Request failed: {r.status_code} {r.text}"
    return r.json()["translated_text"]


def test_short_text():
    result = translate("Hello, how are you?")
    assert len(result) > 0


def test_multi_sentence_under_limit():
    # Two short sentences that fit in one chunk
    text = "The sky is blue. The grass is green."
    result = translate(text)
    assert len(result) > 0


def test_long_text_many_sentences():
    # ~1500 chars — forces multiple chunks grouped by sentence boundaries
    sentences = [f"Sentence {i} is about the weather and nature in India." for i in range(1, 20)]
    text = " ".join(sentences)
    assert len(text) > 600
    result = translate(text)
    assert len(result) > 0


def test_oversized_single_sentence():
    # One sentence well over 600 chars — forces word-level splitting
    text = "The " + "history of ancient civilizations spanning thousands of years " * 12 + "is fascinating."
    assert len(text) > 600
    result = translate(text)
    assert len(result) > 0
