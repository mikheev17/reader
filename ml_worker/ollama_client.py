"""
Ollama client for Gemma 3:1b.
Finds words by English level in document text and translates them.
"""

import json
import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b")
TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))


def _generate(prompt: str) -> str:
    """Call Ollama /api/generate and return the full response text."""
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return (data.get("response") or "").strip()
    except requests.RequestException as e:
        logger.exception("Ollama request failed: %s", e)
        raise


def find_words_by_level(document_text: str, english_level: str) -> list[str]:
    """
    Ask Gemma to extract words from the document that match the given CEFR level.
    Returns a list of English words suitable for the user's level.
    """
    # Truncate long documents to avoid token limits
    max_chars = 8000
    text = document_text if len(document_text) <= max_chars else document_text[:max_chars] + "\n[...]"

    prompt = f"""You are a language learning assistant. Given a text and the user's English level (CEFR: {english_level}), extract a list of English words from the text that are appropriate for this level to learn (not too easy, not too hard). Include not only single words, but phrases. Return a JSON object with a single key "words" and a list of strings, e.g. {{"words": ["word1", "word2"]}}. Return nothing else.

Text:
{text}

Level: {english_level}

JSON:"""
    raw = _generate(prompt)
    # Strip markdown code block if present
    code_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
    if code_match:
        raw = code_match.group(1)
    # Try to parse JSON from the response (model might add extra text)
    try:
        # Find JSON object: from first { to matching }
        start = raw.find("{")
        if start >= 0:
            depth = 0
            for i in range(start, len(raw)):
                if raw[i] == "{":
                    depth += 1
                elif raw[i] == "}":
                    depth -= 1
                    if depth == 0:
                        data = json.loads(raw[start : i + 1])
                        words = data.get("words", [])
                        if isinstance(words, list):
                            return [str(w).strip() for w in words if w]
                        break
        data = json.loads(raw)
        words = data.get("words", [])
        return [str(w).strip() for w in words] if isinstance(words, list) else []
    except (json.JSONDecodeError, TypeError):
        logger.warning("Could not parse words from Ollama response: %s", raw[:500])
        return []


def translate_words(words: list[str], target_lang: str = "Russian") -> dict[str, str]:
    """
    Ask Gemma to translate each word to the target language.
    Returns a dict mapping English word -> translation.
    """
    if not words:
        return {}
    # Batch to avoid long prompts
    batch_size = 30
    result = {}
    for i in range(0, len(words), batch_size):
        batch = words[i : i + batch_size]
        word_list = ", ".join(batch)
        prompt = f"""Translate each of these English words to {target_lang}. Return a JSON object mapping each English word to its translation, e.g. {{"word1": "translation1", "word2": "translation2"}}. Use the exact English words as keys. Return nothing else.

Words: {word_list}

JSON:"""
        raw = _generate(prompt)
        code_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
        if code_match:
            raw = code_match.group(1)
        try:
            start = raw.find("{")
            if start >= 0:
                depth = 0
                for i in range(start, len(raw)):
                    if raw[i] == "{":
                        depth += 1
                    elif raw[i] == "}":
                        depth -= 1
                        if depth == 0:
                            data = json.loads(raw[start : i + 1])
                            if isinstance(data, dict):
                                result.update({k.strip(): str(v).strip() for k, v in data.items()})
                            break
        except (json.JSONDecodeError, TypeError):
            logger.warning("Could not parse translations from Ollama response: %s", raw[:500])
    return result


def find_and_translate_words(document_text: str, english_level: str) -> list[dict]:
    """
    Find words by level in the document and translate them.
    Returns a list of {"word": "...", "translation": "..."}.
    """
    words = find_words_by_level(document_text, english_level)
    if not words:
        return []
    translations = translate_words(words)
    return [
        {"word": w, "translation": translations.get(w, "")}
        for w in words
    ]
