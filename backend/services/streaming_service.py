"""Streaming helpers for chat responses."""

from typing import Generator
from fastapi.responses import StreamingResponse


def stream_text_chunks(text: str, chunk_size: int = 256) -> Generator[bytes, None, None]:
    """Yield the response text in byte chunks for streaming."""
    if not text:
        yield b""
        return

    encoded = text.encode("utf-8")
    for start in range(0, len(encoded), chunk_size):
        yield encoded[start : start + chunk_size]


def create_text_streaming_response(text: str, chunk_size: int = 256) -> StreamingResponse:
    """Return a StreamingResponse for a text payload."""
    return StreamingResponse(stream_text_chunks(text, chunk_size), media_type="text/plain")
