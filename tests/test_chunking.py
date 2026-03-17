import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers.translation import _chunk_text
from helpers.config import CHUNK_LIMIT


def test_short_text_is_single_chunk():
    text = "Hello world. How are you?"
    chunks = _chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_sentences_grouped_under_limit():
    # Two 100-char sentences should be grouped into one chunk
    s1 = "A" * 99 + "."
    s2 = "B" * 99 + "."
    chunks = _chunk_text(f"{s1} {s2}")
    assert len(chunks) == 1


def test_sentences_split_when_over_limit():
    # Each sentence is ~400 chars; two together exceed 600
    s1 = "A" * 399 + "."
    s2 = "B" * 399 + "."
    chunks = _chunk_text(f"{s1} {s2}")
    assert len(chunks) == 2
    assert chunks[0] == s1
    assert chunks[1] == s2


def test_oversized_sentence_is_word_split():
    # A single sentence longer than CHUNK_LIMIT must be split at word boundaries
    long_sentence = " ".join(["word"] * 200)  # well over 600 chars
    chunks = _chunk_text(long_sentence)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= CHUNK_LIMIT
    # Reassembled text preserves all words
    assert " ".join(chunks).split() == long_sentence.split()


def test_mixed_normal_and_oversized():
    # S1(100) + S2(100) | S3(1000) split into 2 | S4(100) + S5(100)
    s_small = lambda c: c * 99 + "."
    s1, s2, s4, s5 = s_small("A"), s_small("B"), s_small("D"), s_small("E")
    s3 = " ".join(["word"] * 150)  # ~750 chars, over CHUNK_LIMIT

    text = f"{s1} {s2} {s3}. {s4} {s5}"
    chunks = _chunk_text(text)

    assert len(chunks) == 4
    assert chunks[0] == f"{s1} {s2}"
    assert chunks[-1] == f"{s4} {s5}"
    for chunk in chunks:
        assert len(chunk) <= CHUNK_LIMIT
