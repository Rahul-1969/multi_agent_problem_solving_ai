"""
llm/ollama_client.py
Robust Ollama LLM client.

Fixes
-----
- _MAX_RETRIES reduced to 1 (was 2) — on CPU, timeout means slow model,
  not broken connection. Retry wastes double the time: 300s + 300s = 10 min.
- Bare `exc` variable reference bug fixed in except blocks.
- requests.Session() reused across calls for connection pooling.
"""

import json
import logging
import time
import requests
import asyncio
from typing import Final

from config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL
from utils.cache import cached_llm_call
from utils.logger import get_logger

logger = get_logger(__name__)

# Module-level Ollama client constants
MODEL_NAME: Final[str] = OLLAMA_MODEL
REQUEST_TIMEOUT: Final[float] = OLLAMA_TIMEOUT
MAX_RETRIES: Final[int] = 1
INITIAL_BACKOFF_SECONDS: Final[float] = 2.0
BACKOFF_FACTOR: Final[int] = 2
OLLAMA_ENDPOINT: Final[str] = OLLAMA_URL

_SESSION: requests.Session = requests.Session()


def _call_llm_uncached(
    prompt: str,
    system: str = "",
    num_predict: int = 512,
    temperature: float = 0.3,
) -> str:
    """
    Call the local Ollama LLM once, without caching.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    if system:
        payload["system"] = system

    backoff = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            resp = _SESSION.post(OLLAMA_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()

            try:
                data = resp.json()
            except ValueError:
                data = None

            if isinstance(data, dict) and "response" in data:
                full_response = _deduplicate(str(data["response"]).strip())
            else:
                full_response = _parse_ollama_response(resp.text.strip())

            if full_response:
                return full_response
            logger.warning("Empty response from Ollama (attempt %d)", attempt)

        except requests.exceptions.ConnectionError:
            logger.exception("Ollama connection error on attempt %d", attempt)
        except requests.exceptions.Timeout:
            logger.warning(
                "Ollama timed out after %.1fs on attempt %d",
                REQUEST_TIMEOUT,
                attempt,
            )
        except requests.exceptions.HTTPError as exc:
            logger.exception("Ollama HTTP error on attempt %d: %s", attempt, exc)
            break
        except requests.exceptions.RequestException as exc:
            logger.exception("Ollama request error on attempt %d: %s", attempt, exc)
            break
        except Exception as exc:
            logger.exception("Unexpected Ollama error on attempt %d: %s", attempt, exc)
            break

        if attempt <= MAX_RETRIES:
            time.sleep(backoff)
            backoff *= BACKOFF_FACTOR

    logger.error(
        "Could not get a response from Ollama (%s) after %d attempts.",
        OLLAMA_ENDPOINT,
        MAX_RETRIES + 1,
    )
    return ""


_cached_call = cached_llm_call(maxsize=256)(_call_llm_uncached)


def call_llm(
    prompt: str,
    system: str = "",
    num_predict: int = 512,
    temperature: float = 0.3,
    domain: str = "",
) -> str:
    """
    Cached wrapper for calling the local Ollama LLM.
    """
    prompt = prompt.strip()
    system = system.strip()
    result = _cached_call(prompt, system, num_predict, temperature, domain=domain)
    if domain:
        logger.debug("Cache hit | domain=%s", domain)
    return result


async def async_call_llm(
    prompt: str,
    system: str = "",
    num_predict: int = 512,
    temperature: float = 0.3,
    domain: str = "",
) -> str:
    """
    Async wrapper that delegates to the sync ``call_llm`` via
    ``asyncio.to_thread`` so async callers do not block the event loop.
    """
    prompt = prompt.strip()
    system = system.strip()
    return await asyncio.to_thread(
        _cached_call, prompt, system, num_predict, temperature, domain
    )


def stream_llm(
    prompt: str,
    system: str = "",
    num_predict: int = 512,
    temperature: float = 0.3,
):
    """
    Stream tokens from the local Ollama LLM.

    Yields text chunks as they arrive from the model.
    Falls back to the non-streaming path if Ollama returns
    a single JSON payload.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt.strip(),
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    if system:
        payload["system"] = system.strip()

    try:
        with _SESSION.post(
            OLLAMA_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT, stream=True
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                chunk = obj.get("response", "")
                if chunk:
                    yield chunk
                if obj.get("done", False):
                    break
    except requests.exceptions.RequestException:
        logger.exception("Ollama streaming request failed")
        # Fall back to non-streaming so the caller still gets an answer
        yield call_llm(prompt, system, num_predict, temperature)


def _parse_ollama_response(raw: str) -> str:
    """Handle both single-JSON and NDJSON Ollama responses."""
    # Try single JSON first (fastest path)
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and "response" in obj:
            return _deduplicate(obj["response"].strip())
    except json.JSONDecodeError:
        pass

    # NDJSON fallback
    parts = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        chunk = obj.get("response", "")
        if chunk:
            parts.append(chunk)
        if obj.get("done", False):
            break

    return _deduplicate("".join(parts).strip())


def _deduplicate(text: str) -> str:
    """Remove duplicated response bodies — known Ollama quirk."""
    if len(text) < 300:
        return text
    mid = len(text) // 2
    w1  = set(text[:mid].lower().split())
    w2  = set(text[mid:].lower().split())
    if not w1 or not w2:
        return text
    overlap = len(w1 & w2) / max(len(w1), len(w2))
    if overlap > 0.95:
        logger.warning("Duplicated LLM response detected — trimming to first half.")
        return text[:mid].strip()
    return text
