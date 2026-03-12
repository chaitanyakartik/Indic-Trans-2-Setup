# IndicTrans2 Translation API

FastAPI server wrapping AI4Bharat's IndicTrans2 models for translation across all 22 scheduled Indian languages.

---

## Folder Structure

```
trans-model/
├── app.py                  # FastAPI server
├── requirements.txt
├── test.py
├── IndicTransToolkit/      # Cloned from VarunGumma/IndicTransToolkit
└── trans-env/              # Python venv
```

---

## Setup

### 1. Create and activate venv
```bash
python3 -m venv trans-env
source trans-env/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install IndicTransToolkit
```bash
git clone https://github.com/VarunGumma/IndicTransToolkit
cd IndicTransToolkit
pip install -e .
cd ..
```
> ⚠️ Note: The old `AI4Bharat/IndicTransToolkit` repo no longer exists. Use `VarunGumma/IndicTransToolkit`.

### 4. HuggingFace login (required — models are gated)
```bash
huggingface-cli login
```
Get your token from https://huggingface.co/settings/tokens, then accept model terms at:
- https://huggingface.co/ai4bharat/indictrans2-en-indic-1B
- https://huggingface.co/ai4bharat/indictrans2-indic-en-1B
- https://huggingface.co/ai4bharat/indictrans2-indic-indic-1B

### 5. Set API key
```bash
export TRANSLATION_API_KEY="your-secret-key-here"
```

### 6. Run the server
```bash
python app.py
```
Server starts on `http://0.0.0.0:8050`. Model loading takes a few minutes on first run.

### 7. (Optional) Expose via ngrok
```bash
ngrok config add-authtoken YOUR_TOKEN
ngrok http 8050
```

---

## Authentication

All requests to `/translate` require an `X-API-Key` header:

```
X-API-Key: your-secret-key-here
```

Set the key via the `TRANSLATION_API_KEY` environment variable before starting the server. Requests without a valid key return `403 Forbidden`.

---

## API Reference

### `POST /translate`

Translate text between any supported language pair.

**Headers**
| Header | Required | Value |
|--------|----------|-------|
| `Content-Type` | Yes | `application/json` |
| `X-API-Key` | Yes | Your API key |

**Request Body**
```json
{
  "source_language": "eng_Latn",
  "target_language": "kan_Knda",
  "text": "Hello, how are you?"
}
```

**Response**
```json
{
  "translated_text": "ಹಲೋ, ನೀವು ಹೇಗಿದ್ದೀರಿ?"
}
```

**Example (curl)**
```bash
curl -X POST https://your-ngrok-url/translate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"source_language": "eng_Latn", "target_language": "hin_Deva", "text": "Good morning"}'
```

**Example (Python)**
```python
import requests

response = requests.post(
    "https://your-ngrok-url/translate",
    headers={"X-API-Key": "your-secret-key-here"},
    json={
        "source_language": "eng_Latn",
        "target_language": "hin_Deva",
        "text": "Good morning"
    }
)
print(response.json()["translated_text"])
```

---

### `GET /health`

Check if server and models are ready. No auth required.

```bash
curl https://your-ngrok-url/health
```

**Response (ready)**
```json
{"status": "ok", "models_loaded": true, "device": "cuda"}
```

**Response (still loading)**
```json
503 - "Models still loading"
```

---

## Supported Languages

Language codes follow the **FLORES-200** format: `{language}_{script}`.

| Language | Code |
|----------|------|
| English | `eng_Latn` |
| Hindi | `hin_Deva` |
| Bengali | `ben_Beng` |
| Gujarati | `guj_Gujr` |
| Kannada | `kan_Knda` |
| Malayalam | `mal_Mlym` |
| Marathi | `mar_Deva` |
| Odia | `ory_Orya` |
| Punjabi | `pan_Guru` |
| Tamil | `tam_Taml` |
| Telugu | `tel_Telu` |
| Urdu | `urd_Arab` |
| Assamese | `asm_Beng` |
| Kashmiri (Devanagari) | `kas_Deva` |
| Kashmiri (Arabic) | `kas_Arab` |
| Konkani | `gom_Deva` |
| Maithili | `mai_Deva` |
| Manipuri (Bengali) | `mni_Beng` |
| Manipuri (Meitei) | `mni_Mtei` |
| Nepali | `npi_Deva` |
| Sanskrit | `san_Deva` |
| Santali | `sat_Olck` |
| Sindhi (Devanagari) | `snd_Deva` |
| Sindhi (Arabic) | `snd_Arab` |
| Bodo | `brx_Deva` |
| Dogri | `dgo_Deva` |

**Model routing is automatic** based on language pair:
- `eng_Latn` → any Indic = `en-indic` model
- any Indic → `eng_Latn` = `indic-en` model
- Indic → Indic = `indic-indic` model

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (empty text, unsupported language pair) |
| 403 | Invalid or missing API key |
| 500 | Translation failed (check server logs) |
| 503 | Models still loading — retry in a minute |o
