import re
import torch
import logging
from .config import DEVICE, CHUNK_LIMIT
from .state import state

logger = logging.getLogger(__name__)


def get_model_key(src_lang: str, tgt_lang: str) -> str:
    """Determine which model to use based on language pair."""
    if src_lang == "eng_Latn" and tgt_lang != "eng_Latn":
        return "en-indic"
    elif src_lang != "eng_Latn" and tgt_lang == "eng_Latn":
        return "indic-en"
    elif src_lang != "eng_Latn" and tgt_lang != "eng_Latn":
        return "indic-indic"
    else:
        raise ValueError("eng_Latn to eng_Latn translation not supported")


def _chunk_text(text: str) -> list:
    """Chunk at sentence boundaries; word-split any sentence > CHUNK_LIMIT."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current = []
    current_len = 0

    for sentence in sentences:
        s_len = len(sentence)

        if s_len > CHUNK_LIMIT:
            # Flush any accumulated sentences first
            if current:
                chunks.append(' '.join(current))
                current = []
                current_len = 0
            # Word-split the oversized sentence
            words = sentence.split()
            sub = []
            sub_len = 0
            for word in words:
                needed = len(word) + (1 if sub else 0)
                if sub_len + needed > CHUNK_LIMIT:
                    chunks.append(' '.join(sub))
                    sub = [word]
                    sub_len = len(word)
                else:
                    sub.append(word)
                    sub_len += needed
            if sub:
                chunks.append(' '.join(sub))

        else:
            space = 1 if current else 0
            if current_len + space + s_len <= CHUNK_LIMIT:
                current.append(sentence)
                current_len += space + s_len
            else:
                chunks.append(' '.join(current))
                current = [sentence]
                current_len = s_len

    if current:
        chunks.append(' '.join(current))

    return chunks


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text of any length by chunking at sentence boundaries."""
    if not state.models_loaded or state.ip is None:
        raise RuntimeError("Models not loaded yet")

    model_key = get_model_key(src_lang, tgt_lang)
    bundle = state.models[model_key]

    chunks = _chunk_text(text)
    logger.info(f"Translating batch of {len(chunks)} chunk(s) for {len(text)} chars")

    # Translate all chunks in one GPU batch call
    batch = state.ip.preprocess_batch(chunks, src_lang=src_lang, tgt_lang=tgt_lang)
    inputs = bundle["tokenizer"](
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
        return_attention_mask=True,
    ).to(DEVICE)
    with torch.no_grad():
        tokens = bundle["model"].generate(**inputs, max_length=256, num_beams=5)
    decoded = bundle["tokenizer"].batch_decode(
        tokens, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )
    translations = state.ip.postprocess_batch(decoded, lang=tgt_lang)
    return ' '.join(translations)
