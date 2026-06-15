from backend.services.streaming_service import stream_text_chunks


def test_stream_text_chunks_yields_expected_parts():
    text = "Hello world! This is a test."
    chunks = list(stream_text_chunks(text, chunk_size=10))

    assert b"Hello worl" in chunks
    assert b"d! This is" in chunks
    assert b" a test." in chunks
    assert b"" not in chunks


def test_stream_text_chunks_empty_string():
    chunks = list(stream_text_chunks("", chunk_size=10))
    assert chunks == [b""]
