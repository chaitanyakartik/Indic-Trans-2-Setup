"""
Maps IndicTrans2 language codes to Google Cloud Speech/TTS codes and voice names.
"""

GOOGLE_LANG_MAP = {
    "eng_Latn": {"stt": "en-US", "tts_lang": "en-US", "tts_voice": "en-US-Chirp3-HD-Aoede"},
    "hin_Deva": {"stt": "hi-IN", "tts_lang": "hi-IN", "tts_voice": "hi-IN-Chirp3-HD-Aoede"},
    "kan_Knda": {"stt": "kn-IN", "tts_lang": "kn-IN", "tts_voice": "kn-IN-Chirp3-HD-Aoede"},
    "tam_Taml": {"stt": "ta-IN", "tts_lang": "ta-IN", "tts_voice": "ta-IN-Chirp3-HD-Aoede"},
    "tel_Telu": {"stt": "te-IN", "tts_lang": "te-IN", "tts_voice": "te-IN-Chirp3-HD-Aoede"},
    "ben_Beng": {"stt": "bn-IN", "tts_lang": "bn-IN", "tts_voice": "bn-IN-Chirp3-HD-Aoede"},
    "mar_Deva": {"stt": "mr-IN", "tts_lang": "mr-IN", "tts_voice": "mr-IN-Chirp3-HD-Aoede"},
    "guj_Gujr": {"stt": "gu-IN", "tts_lang": "gu-IN", "tts_voice": "gu-IN-Chirp3-HD-Aoede"},
    "pan_Guru": {"stt": "pa-IN", "tts_lang": "pa-IN", "tts_voice": "pa-IN-Chirp3-HD-Aoede"},
    "mal_Mlym": {"stt": "ml-IN", "tts_lang": "ml-IN", "tts_voice": "ml-IN-Chirp3-HD-Aoede"},
}


def get_google_codes(indic_code: str) -> dict:
    if indic_code not in GOOGLE_LANG_MAP:
        raise ValueError(f"Unsupported language for audio/speech: {indic_code}")
    return GOOGLE_LANG_MAP[indic_code]
