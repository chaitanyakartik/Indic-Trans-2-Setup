# IndicTrans2 Translation API

FastAPI server wrapping AI4Bharat's IndicTrans2 models for translation across Indian languages, with OCR support for scanned documents and Google Cloud Speech/TTS for audio.

---

## Architecture

Two services run in separate virtual environments:

| Service | File | venv | Port |
|---------|------|------|------|
| Translation API | `main.py` | `trans-env` | 8003 |
| OCR Service (Surya) | `ocr/ocr_server.py` | `surya_env` | 8010 |

```
Indic-Trans-2-Setup/
├── main.py                  # Translation API (FastAPI)
├── ocr/
│   └── ocr_server.py        # Surya OCR microservice
├── helpers/
│   ├── config.py            # DEVICE, API_KEY, OCR/Google config
│   ├── state.py             # App state (model handles)
│   ├── model_loader.py      # Loads IndicTrans2 models into VRAM
│   ├── translation.py       # Text chunking + batched translation
│   ├── pdf_utils.py         # PyMuPDF extraction + OCR fallback
│   ├── audio_utils.py       # ffmpeg conversion, Google STT/TTS
│   ├── lang_map.py          # IndicTrans2 ↔ Google language code mapping
│   └── schemas.py           # Pydantic request/response models
├── tests/
│   ├── test_scanned_pdf.py
│   └── load_test.py
├── keys/
│   └── gok-ipgrs-voice-sa.json   # Google Cloud service account (not committed)
├── logs/                    # Server logs (*.txt gitignored)
├── requirements.txt
└── surya_requirements.txt
```

---

## Setup

### 1. Translation API (trans-env)

```bash
python3 -m venv trans-env
source trans-env/bin/activate
pip install -r requirements.txt
```

Install IndicTransToolkit:
```bash
git clone https://github.com/VarunGumma/IndicTransToolkit
cd IndicTransToolkit && pip install -e . && cd ..
```

HuggingFace login (models are gated):
```bash
huggingface-cli login
```
Accept model terms at:
- https://huggingface.co/ai4bharat/indictrans2-en-indic-1B
- https://huggingface.co/ai4bharat/indictrans2-indic-en-1B
- https://huggingface.co/ai4bharat/indictrans2-indic-indic-1B

### 2. OCR Service (surya_env)

```bash
python3 -m venv surya_env
source surya_env/bin/activate
pip install -r surya_requirements.txt
```

### 3. Google Cloud credentials (for audio endpoints)

Place your Google Cloud service account JSON at:
```
keys/gok-ipgrs-voice-sa.json
```
Or set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
```

### 4. Start both services

**Terminal 1 — OCR service:**
```bash
source surya_env/bin/activate
python ocr/ocr_server.py
```

**Terminal 2 — Translation API:**
```bash
source trans-env/bin/activate
python main.py
```

Models load into VRAM at startup (takes ~1–2 minutes). Check readiness:
```bash
curl http://localhost:8003/health
```

---

## Authentication

All endpoints except `/health` and `/help` require an API key header:

```
X-API-Key: your-secret-key-here
```

The key is configured in `helpers/config.py`.

---

## API Reference

### `GET /health`

Check server and model readiness. No auth required.

```bash
curl http://localhost:8003/health
```

```json
{"status": "ok", "models_loaded": true, "device": "cuda"}
```

---

### `POST /translate`

Translate text between any supported language pair. Long text is automatically chunked and batched.

```bash
curl -X POST http://localhost:8003/translate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"source_language": "eng_Latn", "target_language": "kan_Knda", "text": "Hello, how are you?"}'
```

**Request**
```json
{
  "source_language": "eng_Latn",
  "target_language": "kan_Knda",
  "text": "Input text of any length"
}
```

**Response**
```json
{"translated_text": "ಹಲೋ, ನೀವು ಹೇಗಿದ್ದೀರಿ?"}
```

---

### `POST /translate-pdf`

Extract text from a PDF and translate it. Handles both text-layer PDFs and scanned/image PDFs (via OCR — requires the OCR service to be running).

```bash
curl -X POST http://localhost:8003/translate-pdf \
  -H "X-API-Key: your-key" \
  -F "file=@document.pdf" \
  -F "source_language=kan_Knda" \
  -F "target_language=eng_Latn"
```

**Response**
```json
{"translated_text": "..."}
```

Mixed PDFs (some text pages, some scanned) are handled page-by-page — text pages use PyMuPDF directly, scanned pages go through Surya OCR.

---

### `POST /translate-image`

OCR an image and translate the extracted text. Requires the OCR service to be running.

```bash
curl -X POST http://localhost:8003/translate-image \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "image_b64": "<base64-encoded image>",
    "source_language": "kan_Knda",
    "target_language": "eng_Latn"
  }'
```

**Response**
```json
{"translated_text": "..."}
```

---

### `POST /translate-audio`

Transcribe audio, translate the transcript, and synthesize speech in the target language. Requires Google Cloud credentials.

- Input: any audio format supported by ffmpeg (MP3, OGG, WAV, M4A, etc.)
- Output: translated text + MP3 audio (base64-encoded)

```bash
curl -X POST http://localhost:8003/translate-audio \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "audio_b64": "<base64-encoded audio>",
    "source_language": "kan_Knda",
    "target_language": "eng_Latn"
  }'
```

**Response**
```json
{
  "translated_text": "...",
  "audio_b64": "<base64-encoded MP3>"
}
```

---

### `GET /help`

Returns API documentation and all supported language codes. No auth required.

---

## Supported Languages

Language codes follow the FLORES-200 format. The audio endpoints (STT/TTS) support the 10 languages below. The translation engine supports all 22 scheduled Indian languages.

| Language | Code | Audio supported |
|----------|------|:--------------:|
| English | `eng_Latn` | Yes |
| Hindi | `hin_Deva` | Yes |
| Kannada | `kan_Knda` | Yes |
| Tamil | `tam_Taml` | Yes |
| Telugu | `tel_Telu` | Yes |
| Bengali | `ben_Beng` | Yes |
| Marathi | `mar_Deva` | Yes |
| Gujarati | `guj_Gujr` | Yes |
| Punjabi | `pan_Guru` | Yes |
| Malayalam | `mal_Mlym` | Yes |
| Assamese | `asm_Beng` | |
| Odia | `ory_Orya` | |
| Urdu | `urd_Arab` | |
| Sanskrit | `san_Deva` | |
| ... and more | | |

Model routing is automatic:
- `eng_Latn` → Indic: `en-indic` model
- Indic → `eng_Latn`: `indic-en` model
- Indic → Indic: `indic-indic` model

---

## Logging

Logs are written to both the terminal and `logs/log.txt` in the format:
```
2026-03-18 12:00:00,123 INFO: Page 1: text extracted (342 chars)
```

The `logs/` directory is tracked in git but `logs/*.txt` files are gitignored.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (empty input, unsupported language pair, OCR returned no text) |
| 403 | Invalid or missing API key |
| 500 | Internal error (check `logs/log.txt`) |
| 503 | Models still loading, or OCR/audio service unavailable |
