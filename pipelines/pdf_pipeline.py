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
from llm.ollama_client import call_llm
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


def pdf_pipeline(query: str, chunks: list[dict], filename: str) -> str:
    """
    Answer a question from the loaded PDF with page references.
    """
    if not chunks:
        return (
            "📄  No PDF is currently loaded.\n\n"
            "To load a PDF, type:\n"
            "    load pdf <path>\n\n"
            "Example:\n"
            "    load pdf C:\\Users\\HP\\Documents\\notes.pdf"
        )

    # ── Step 1: Retrieve relevant chunks ─────────────────────────────────────
    chunks = retrieve_chunks(query, chunks, top_n=4)

    if not chunks:
        return (
            f"🔍  No relevant content found in '{filename}' "
            f"for your query.\n\n"
            "Try rephrasing with keywords that appear in the document."
        )

    context = _format_context(chunks)
    ref_pages = sorted(set(c["page_num"] for c in chunks))

    # ── Step 2: Build grounded prompt ────────────────────────────────────────
    prompt = (
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

    # ── Step 3: LLM call ──────────────────────────────────────────────────────
    try:
        logger.info("PDF pipeline: querying '%s' | query: %s",
                    filename, query[:60])
        raw = call_llm(prompt=prompt, system=_SYSTEM)
    except RuntimeError as exc:
        logger.error("PDF pipeline LLM error: %s", exc)
        return f"⚠️  LLM unavailable.\nError: {exc}"

    # ── Step 4: Parse and format output ──────────────────────────────────────
    answer     = _extract_tag(raw, "answer")
    references = _extract_tag(raw, "references")

    # Fallback if model skipped tags
    if not answer:
        logger.warning("PDF pipeline: LLM skipped tags — showing raw output")
        answer = raw.strip()

    # Build page reference line from retrieved chunks (always accurate)
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