"""
Audio utilities: ffmpeg format conversion, Google Speech-to-Text, Google Text-to-Speech.
Google credentials are configured via GOOGLE_APPLICATION_CREDENTIALS (set in config.py).
"""
import asyncio
import logging
import os
import tempfile

from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as tts

logger = logging.getLogger(__name__)


async def convert_to_wav(audio_bytes: bytes) -> bytes:
    """Convert any audio format to 16kHz mono PCM WAV using ffmpeg."""
    with tempfile.NamedTemporaryFile(suffix=".in", delete=False) as fin:
        fin.write(audio_bytes)
        in_path = fin.name

    out_path = in_path + ".wav"
    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/ffmpeg", "-y", "-i", in_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", "-acodec", "pcm_s16le",
            out_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("ffmpeg audio conversion failed")
        with open(out_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(in_path):
            os.unlink(in_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def _stt_blocking(wav_bytes: bytes, language_code: str) -> str:
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    audio = speech.RecognitionAudio(content=wav_bytes)
    response = client.recognize(config=config, audio=audio)
    transcription = "\n".join(
        result.alternatives[0].transcript
        for result in response.results
        if result.alternatives
    )
    return transcription


async def speech_to_text(wav_bytes: bytes, language_code: str) -> str:
    """Transcribe WAV audio using Google Speech-to-Text."""
    logger.info(f"STT: transcribing {len(wav_bytes)//1024}KB WAV, lang={language_code}")
    text = await asyncio.to_thread(_stt_blocking, wav_bytes, language_code)
    logger.info(f"STT: got {len(text)} chars")
    return text


def _tts_blocking(text: str, language_code: str, voice_name: str) -> bytes:
    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=tts.SynthesisInput(text=text),
        voice=tts.VoiceSelectionParams(language_code=language_code, name=voice_name),
        audio_config=tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3),
    )
    return response.audio_content


async def text_to_speech(text: str, language_code: str, voice_name: str) -> bytes:
    """Synthesize speech using Google Text-to-Speech, returns MP3 bytes."""
    logger.info(f"TTS: synthesizing {len(text)} chars, lang={language_code}, voice={voice_name}")
    mp3 = await asyncio.to_thread(_tts_blocking, text, language_code, voice_name)
    logger.info(f"TTS: got {len(mp3)//1024}KB MP3")
    return mp3
