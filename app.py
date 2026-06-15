"""
app.py
Multi-Agent AI Chatbot — Main Entry Point

Architecture
------------
User Query
  └─► PDF command?   → load/clear PDF commands handled first
  └─► PDF loaded?    → pdf_pipeline (grounded QA with references)
  └─► Domain Router  (keyword-based, ~0 ms)
        ├─► College Pipeline    (rule-based extractor + dataset predictor, <1s)
        ├─► Medical Pipeline    (single-agent structured LLM)
        ├─► Coding Pipeline     (multi-agent LLM, complexity-aware)
        ├─► Education Pipeline  (single-agent structured LLM, student-focused)
        └─► General Pipeline    (multi-agent LLM, complexity-aware)

PDF Commands (handled before routing)
--------------------------------------
  load pdf <path>   — load a PDF for Q&A
  pdf info          — show current PDF info
  clear pdf         — unload current PDF
  exit / quit / bye — exit chatbot
"""

import os
import sys
import time

from backend.services.chatbot_service import process_query
from utils.logger import get_logger, setup_logging
from backend.models.response_models import ChatResponse
from tools.data_loader import load_data
from tools.pdf_store import pdf_store

setup_logging()
logger = get_logger("chatbot")

EXIT_COMMANDS = {"exit", "quit", "bye"}

# ── Warm-up ───────────────────────────────────────────────────────────────────
def _warmup():
    try:
        logger.info("Pre-loading EAMCET dataset …")

        t = time.time()

        df = load_data()

        logger.info(
            "Dataset ready (%d records, %.2f s)",
            len(df),
            time.time() - t
        )

    except Exception:
        logger.exception(
            "Failed to preload dataset"
        )

_DIVIDER = "─" * 60

# ── PDF command handler ───────────────────────────────────────────────────────
def _handle_pdf_command(query: str) -> str | None:
    """
    Intercepts PDF management commands before domain routing.
    Returns response string if it's a PDF command, else None.
    """
    q = query.strip()
    ql = q.lower()

    # ── load pdf <path> ───────────────────────────────────────────────────────
    if ql.startswith("load pdf "):
        path = q[9:].strip().strip('"').strip("'")
        if not path:
            return "Usage: load pdf <full path to PDF file>"
        if not os.path.exists(path):
            return f"❌  File not found: {path}"
        try:
            info = pdf_store.load(path)
            return (
                f"✅  PDF loaded successfully!\n"
                f"   File   : {info['filename']}\n"
                f"   Pages  : {info['pages']}\n"
                f"   Chunks : {info['chunks']}\n\n"
                f"You can now ask questions about this document."
            )
        except Exception:
            logger.exception("Failed to load PDF")

            return (
                "❌ Failed to load PDF.\n"
                "Please verify that the file is a valid PDF."
            )

    # ── pdf info ──────────────────────────────────────────────────────────────
    if ql in ("pdf info", "pdf status", "show pdf"):
        if pdf_store.is_loaded():
            return (
                f"📄  Loaded PDF: {pdf_store.filename}\n"
                f"    Pages  : {pdf_store.page_count}\n"
                f"    Chunks : {len(pdf_store.chunks)}"
            )
        return "📄  No PDF is currently loaded.\n   Use: load pdf <path>"

    # ── clear pdf ─────────────────────────────────────────────────────────────
    if ql in ("clear pdf", "unload pdf", "remove pdf"):
        if pdf_store.is_loaded():
            name = pdf_store.filename
            pdf_store.clear()
            return f"🗑️  PDF '{name}' has been unloaded."
        return "No PDF is currently loaded."

    # ── help ──────────────────────────────────────────────────────────────────
    if ql in ("help", "?", "commands"):
        return (
            "📋  Available Commands\n"
            + "─" * 40 + "\n"
            + "  load pdf <path>  — Load a PDF for Q&A\n"
            + "  pdf info         — Show loaded PDF info\n"
            + "  clear pdf        — Unload current PDF\n"
            + "  exit / quit      — Exit the chatbot\n"
            + "─" * 40 + "\n"
            + "  Just type any question to chat!"
        )

    return None   # not a PDF command


# ── Core chatbot ──────────────────────────────────────────────────────────────
def chatbot(query: str) -> str:
    if not query.strip():
        return "Please enter a query."

    # Step 1: PDF commands take highest priority
    pdf_cmd_result = _handle_pdf_command(query)
    if pdf_cmd_result is not None:
        return pdf_cmd_result
    # Delegate to service layer (single execution path)
    result: ChatResponse = process_query(query)

    logger.info(
        "Domain=%s | Query=%s",
        result.domain,
        query[:80]
    )

    if not result.success and result.error:
        return result.error

    return result.response


# ── CLI loop ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(_DIVIDER)
    print("  Multi-Agent AI Chatbot  |  TG EAMCET Predictor Edition")
    print("  Type 'help' for commands or 'exit' to quit.")
    print(_DIVIDER)

    _warmup()
    print("\nChatbot is ready. Ask me anything!\n")

    while True:
        # Show PDF indicator in prompt if a PDF is loaded
        prompt_label = (
            f"[PDF:{pdf_store.filename}] You: "
            if pdf_store.is_loaded()
            else "You: "
        )

        try:
            query = input(prompt_label).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            sys.exit(0)

        if not query:
            continue

        if query.lower() in EXIT_COMMANDS:
            print("Bot: Goodbye! All the best!")
            sys.exit(0)

        t0 = time.time()
        response = chatbot(query)
        elapsed = time.time() - t0

        print(f"\nBot:\n{response}")
        print(f"\n  ⏱  Response time: {elapsed:.2f}s\n")
        print(_DIVIDER)