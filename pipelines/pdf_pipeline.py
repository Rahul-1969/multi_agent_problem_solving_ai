"""
pipelines/pdf_pipeline.py
Answers user questions from an uploaded PDF with page references.

Flow
----
1. Retrieve top-N relevant chunks using keyword scoring (pdf_retriever)
2. Build a grounded prompt: "Answer ONLY from this context: ..."
3. Single LLM call → structured answer + references
4. Parse <answer> and <references> tags → formatted output

The prompt enforces grounding: if the answer isn't in the PDF,
the LLM is instructed to say so rather than hallucinate.
"""

from utils.logger import get_logger
import re
from llm.ollama_client import call_llm, async_call_llm
from tools.pdf_retriever import retrieve_chunks

logger = get_logger(__name__)

_DIVIDER = "─" * 55

_SYSTEM = (
    "You are a precise document assistant. "
    "Answer questions STRICTLY based on the provided context passages. "
    "Do NOT use outside knowledge. "
    "If the answer is not in the context, say: 'This information is not found in the uploaded document.' "
    "Plain text only. Be concise."
)


def _format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[Passage {i} — Page {c['page_num']}]\n{c['text']}")
    return "\n\n".join(parts)


def _extract_tag(text: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _build_pdf_prompt(query: str, chunks: list[dict], filename: str) -> str:
    """Build the grounded prompt for PDF Q&A."""
    context = _format_context(chunks)
    return (
        f"Document: {filename}\n\n"
        f"Context passages from the document:\n\n"
        f"{context}\n\n"
        f"Question: {query}\n\n"
        "Answer using ONLY the context above. Use this structure:\n\n"
        "<answer>\n"
        "Your complete answer here, based strictly on the context.\n"
        "</answer>\n\n"
        "<references>\n"
        "List the specific page numbers and a short quote (max 15 words) "
        "that support your answer.\n"
        "</references>"
    )


def _format_pdf_response(raw: str, ref_pages: list[int], filename: str) -> str:
    """Format the LLM raw output into the final response string."""
    answer = _extract_tag(raw, "answer")
    references = _extract_tag(raw, "references")

    if not answer:
        logger.warning("PDF pipeline: LLM skipped tags — showing raw output")
        answer = raw.strip()

    pages_line = ", ".join(f"Page {p}" for p in ref_pages)

    lines = [
        f"📄  ANSWER FROM: {filename}",
        _DIVIDER,
        "",
        answer,
        "",
        _DIVIDER,
        f"📌  References: {pages_line}",
    ]

    if references:
        lines += ["", "📝  Cited passages:", references]

    return "\n".join(lines)


def _prepare_pdf_pipeline(query: str, chunks: list[dict], filename: str):
    """Shared preparation for PDF Q&A. Returns (prompt, ref_pages, early_result)."""
    if not chunks:
        early = (
            "📄  No PDF is currently loaded.\n\n"
            "To load a PDF, type:\n"
            "    load pdf <path>\n\n"
            "Example:\n"
            "    load pdf C:\\Users\\HP\\Documents\\notes.pdf"
        )
        return None, None, early

    chunks = retrieve_chunks(query, chunks, top_n=4)

    if not chunks:
        early = (
            f"🔍  No relevant content found in '{filename}' "
            f"for your query.\n\n"
            "Try rephrasing with keywords that appear in the document."
        )
        return None, None, early

    prompt = _build_pdf_prompt(query, chunks, filename)
    ref_pages = sorted(set(c["page_num"] for c in chunks))
    return prompt, ref_pages, None


def pdf_pipeline(query: str, chunks: list[dict], filename: str) -> str:
    """Answer a question from the loaded PDF with page references (sync)."""
    prompt, ref_pages, early = _prepare_pdf_pipeline(query, chunks, filename)
    if early:
        return early

    try:
        logger.info("PDF pipeline: querying '%s' | query: %s",
                    filename, query[:60])
        raw = call_llm(prompt=prompt, system=_SYSTEM)
    except RuntimeError as exc:
        logger.error("PDF pipeline LLM error: %s", exc)
        return f"⚠️  LLM unavailable.\nError: {exc}"

    return _format_pdf_response(raw, ref_pages, filename)


async def async_pdf_pipeline(query: str, chunks: list[dict], filename: str) -> str:
    """Answer a question from the loaded PDF with page references (async)."""
    prompt, ref_pages, early = _prepare_pdf_pipeline(query, chunks, filename)
    if early:
        return early

    try:
        logger.info("Async PDF pipeline: querying '%s' | query: %s",
                    filename, query[:60])
        raw = await async_call_llm(prompt=prompt, system=_SYSTEM)
    except RuntimeError as exc:
        logger.error("Async PDF pipeline LLM error: %s", exc)
        return f"⚠️  LLM unavailable.\nError: {exc}"

    return _format_pdf_response(raw, ref_pages, filename)