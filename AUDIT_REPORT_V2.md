# Multi-Agent AI Chatbot — Repository Architecture Audit V2

> **Scope:** Full recursive audit of `backend/`, `frontend/`, `agents/`, `pipelines/`, `router/`, `llm/`, `utils/`, `tools/`, `schemas/`, `constants/`, `config/`, `tests/`  
> **Constraint:** Zero source code modifications.  
> **Date:** 2026-06-20

---

## Table of Contents

1. [Overview](#1-overview)
2. [P0 — Runtime Crashes & Security](#2-p0--runtime-crashes--security)
3. [P1 — Functional Defects & Broken Contracts](#3-p1--functional-defects--broken-contracts)
4. [P2 — Technical Debt & Performance](#4-p2--technical-debt--performance)
5. [P3 — Cleanup & Dead Code](#5-p3--cleanup--dead-code)
6. [Summary & Recommended Order](#6-summary--recommended-order)
7. [Architectural Dependency Graph](#7-architectural-dependency-graph)

---

## 1. Overview

This audit covers every code-bearing file in the repository. Findings are categorized by severity:

| Panel | Meaning | Action |
|-------|---------|--------|
| **P0** | Crash / Security / Data loss | Fix immediately |
| **P1** | Functional defect / Broken contract | Fix before next release |
| **P2** | Tech debt / Performance / Reliability | Fix in current sprint |
| **P3** | Cleanup / Dead code / Minor | Fix when convenient |

**Total unique findings:**
- P0: **19**
- P1: **31**
- P2: **42**
- P3: **28**

---

## 2. P0 — Runtime Crashes & Security

| # | File | Line(s) | Issue | Impact | Fix Complexity |
|---|------|---------|-------|--------|----------------|
| **P0-01** | `backend/api/routes/pdf.py` | 181 | `async_answer_from_pdf` called but **not imported** (only `answer_from_pdf` imported from `pdf_service`). | `NameError` on `/pdf/ask` — endpoint completely broken. | Low |
| **P0-02** | `backend/api/routes/chat.py` | 85, 115 | `chat` and `chat_stream` are `def` (sync) but call `process_query()` → blocking `call_llm()` (240s timeout). Blocks entire FastAPI event loop. | Server unresponsive under load; single user blocks all others. | Medium |
| **P0-03** | `backend/api/routes/college.py` | 20 | Same as P0-02 — sync endpoint calling blocking LLM pipeline. | Event loop blocking. | Medium |
| **P0-04** | `backend/api/routes/coding.py` | 18 | Same as P0-02. | Event loop blocking. | Medium |
| **P0-05** | `backend/api/routes/education.py` | 18 | Same as P0-02. | Event loop blocking. | Medium |
| **P0-06** | `backend/api/routes/medical.py` | 18 | Same as P0-02. | Event loop blocking. | Medium |
| **P0-07** | `backend/auth/jwt_service.py` | 10–12, 25–40 | Single `SECRET_KEY` used for both access (30 min) and refresh (7 day) tokens. No key separation. | Compromised access token → attacker can forge refresh tokens. | Medium |
| **P0-08** | `backend/api/routes/auth.py` | 13, 45, 54, 63, 72, 95, 104, 113 | `secure=False` hardcoded on every cookie. No env control. | Session cookies sent over HTTP in production; hijacking risk. | Low |
| **P0-09** | `backend/api/routes/pdf.py` | 48–55 | `os.path.commonpath` path traversal check does **not resolve symlinks**. | Attacker uploads symlink → arbitrary file read. | Medium |
| **P0-10** | `backend/api/routes/pdf.py` | 88–96 | `os.path.basename(file.filename)` but no validation against null bytes, unicode tricks, or Windows reserved names (`CON`, `PRN`, `NUL`). | File overwrite / OS confusion on Windows. | Low |
| **P0-11** | `backend/auth/jwt_service.py` | 14–17 | `RuntimeError` raised at **import time** if `JWT_SECRET_KEY` env var missing. | App fails to start without env setup; blocks testing. | Low |
| **P0-12** | `backend/auth/user_store.py` | 9–15 | Default admin account ships with hardcoded bcrypt hash (`$2b$12$...`) — corresponds to known password. | Backdoor admin if deployed unchanged. | Low |
| **P0-13** | `llm/ollama_client.py` | 30 | `_SESSION = requests.Session()` created at **module import time**. | Resource leak if module imported but never used. | Low |
| **P0-14** | `config/path_config.py` | 20–25 | `ensure_directories()` runs at module level; directory creation side effect on import. | Unexpected filesystem mutations on import. | Low |
| **P0-15** | `frontend/src/services/authStorage.js` | 16–22 | `saveStoredUser` stores `access_token` and `refresh_token` in `localStorage`, contradicting httpOnly cookie design. | Tokens exposed to XSS. Front-end has full credential theft surface. | Low |
| **P0-16** | `frontend/src/services/pdfService.js` | 28 | `uploadPdf` explicitly sets `Content-Type: multipart/form-data` header — Axios sets this automatically with boundary. Explicit header **breaks multipart** (missing boundary). | PDF uploads fail; `400 Bad Request` from backend. | Low |
| **P0-17** | `frontend/src/store/chatStore.js` | 119–124 | Error handler creates message with **both** `text` AND `content` fields. `MessageBubble` uses `text ?? content` — confusing dual-key pattern. | Inconsistent data model; messages may render incorrectly depending on which key is set. | Low |
| **P0-18** | `frontend/src/store/chatStore.js` | 87 | `postMessage` sends `{ sender: 'user', content: trimmed, domain: 'user' }` but backend `ChatMessage` model expects `text` (not `content`) as the primary field. | Backend validation error or silent data loss on message ingestion. | Low |
| **P0-19** | `pipelines/education_pipeline.py` | 152 | Pipeline `_SECTION_LABELS` uses `"keypoints"` as key but `EDUCATION_LABELS` schema uses `"key_points"` (underscore). | `format_education` in formatter fails to parse pipeline output; structured education data lost. | Low |

---

## 3. P1 — Functional Defects & Broken Contracts

| # | File | Line(s) | Issue | Impact | Fix Complexity |
|---|------|---------|-------|--------|----------------|
| **P1-01** | `backend/api/routes/chat.py` | 108–112 | `chat.get("messages")` returns dicts with `content` key; `ChatMessage` validator maps `content` → `text`. Works but fragile — depends on validator always running. | Validation error if `model_construct` used or validator skipped. | Low |
| **P1-02** | `backend/api/routes/chat.py` | 115–120 | `chat_stream` is sync, calls blocking `process_query()`, then streams already-complete response in chunks. Not true streaming. | No time-to-first-token benefit; misleading UX. | Medium |
| **P1-03** | `router/domain_router.py` | 280–295 | `_EDU_INTENTS` adds +2 boost for generic queries like `"what is"`, `"explain"`. Query `"what is the capital of france"` → misrouted to education. | Non-CS questions waste LLM tokens; poor answer quality. | Medium |
| **P1-04** | `tools/college_predictor.py` | 68–73 | Location filter yields 0 rows → logs `info` and silently retries without location. No user indication. | User sees results for wrong city, thinks predictor failed. | Low |
| **P1-05** | `pipelines/medical_pipeline.py` | 88–100 | `_HIGH_RISK_PATTERNS` mixes tuples `("chest pain", "left arm")` and strings `"fainted"`. Loop logic handles both via `isinstance` — fragile. | Emergency detection silently fails if pattern structure changes. | Low |
| **P1-06** | `pipelines/coding_pipeline.py` | 31–32, 260 | `_CODE_PATTERN` defined at module level but also conceptually shared with `response_formatter.py`. Circular import risk if formatter imports pipeline. | Import-time `NameError` if import order changes. | Low |
| **P1-07** | `backend/services/formatter_dispatcher.py` | 55–65 | If `PipelineResult.data is None`, falls through to `_format()` which parses the **formatted string** — lossy and may fail. | Structured data lost for error/fallback responses. | Low |
| **P1-08** | `backend/models/response_models.py` | 75–77 | `ChatResponse.data` is `ResponseData` union but formatter returns `dict` via `.model_dump()`. Nested models have `extra="forbid"`. | Potential validation errors on response serialization. | Medium |
| **P1-09** | `tools/pdf_session_manager.py` | 55–65 | `_cleanup_if_needed` iterates `self._sessions` and pops stale entries while holding lock. Another `get_store` may mutate dict during iteration. | `RuntimeError: dictionary changed size during iteration` under concurrent PDF load. | Low |
| **P1-10** | `tools/data_loader.py` | 35–65 | Global `_df` cache checked with `if _df is not None: return _df`. No lock on first load. | Concurrent first calls load CSV multiple times; memory/CPU waste. | Low |
| **P1-11** | `agents/extractor_agent.py` | 55–60 | Fallback rank pattern `(?<!\d)(\d{3,6})(?!\d)` matches **any** 3-6 digit number (years, phone numbers). | Query `"in 2024 my rank is 5000"` → extracts `2024` as rank. | Low |
| **P1-12** | `pipelines/coding_pipeline.py` | 130–165 | `validate_coding_query` returns clarification string for unknown algorithms. `coding_pipeline` returns `PipelineResult` with `success` implied True. | Frontend treats clarification as successful answer. | Low |
| **P1-13** | `frontend/src/store/chatStore.js` | 65 | `loadChat` expects `data.chat_id`; `loadChats` returns `id` field. Inconsistent ID names. | Chat detail may fail to map correctly. | Low |
| **P1-14** | `frontend/src/store/chatStore.js` | 78 | `createNewChat` expects `data.chat_id` but backend may return `id`. Same inconsistency. | New chat creation may show wrong ID. | Low |
| **P1-15** | `frontend/src/services/chatService.js` | 35–39 | `sendMessage` spreads `mapChatResponse(response)` then adds `messages` top-level. `chatStore.submitMessage` accesses `result.messages` — fragile. | Breaks if response shape changes slightly. | Low |
| **P1-16** | `frontend/src/pages/Register.jsx` | 37 | On success, navigates to `/login` but does **not auto-login**. User must log in again after registration. | Poor UX; friction. | Low |
| **P1-17** | `frontend/src/store/authStore.js` | 52 | `verifySession` only checks `localStorage`, never calls backend to validate token. | Stale user data persists after server-side logout / token expiry. | Low |
| **P1-18** | `agents/agent_policy.py` | 56 | `should_run_expert` checks `result.confidence >= 0.6` to **skip** expert. Base agent `_estimate_confidence` returns 0.70–0.95 for most answers. | Expert rarely triggers even for high-complexity queries. | Low |
| **P1-19** | `pipelines/coding_pipeline.py` | 227 | `get_close_matches` with `cutoff=0.35` — very loose. Returns irrelevant suggestions (e.g. "bubble" → "fibonacci"). | Poor UX; misleading clarifications. | Low |
| **P1-20** | `pipelines/education_pipeline.py` | 84 | `_build_prompt` includes `"DIAGRAM:"` only for high complexity, but parser `_SECTION_LABELS` always expects it. | Parser creates empty section for low/medium queries. | Low |
| **P1-21** | `pipelines/pdf_pipeline.py` | 119 | `async_pdf_pipeline` delegates to `async_call_llm` which uses `asyncio.to_thread(call_llm)`. `call_llm` is cached; thread pool contention under load. | Still blocks a thread per request; no true async HTTP. | Medium |
| **P1-22** | `llm/ollama_client.py` | 123 | `async_call_llm` wraps sync `call_llm` in `asyncio.to_thread` — defeats async I/O; still blocks a thread. | Thread pool exhaustion under concurrent load. | Medium |
| **P1-23** | `utils/agent_executor.py` | 110 | `_cached_base_result` cache key is query string **only**. Ignores `system` prompt, `num_predict`, model changes. | Stale cached responses if config changes. | Low |
| **P1-24** | `utils/response_formatter.py` | 118 | `format_coding` uses `_CODE_PATTERN` on output that may have been through `clean_text` (strips markdown fences). | Code fence may be removed before formatter runs; parsing fails. | Medium |
| **P1-25** | `utils/response_formatter.py` | 170 | `format_college` expects bullet points with `•` but college pipeline emits custom format with emojis. | Formatter output mismatch; structured data lost. | Medium |
| **P1-26** | `tools/college_predictor.py` | 115 | `predict_colleges` filters `cutoff_rank >= rank` — EAMCET cutoffs are closing ranks. Logic **inverted**: safer colleges have lower cutoff. | Returns colleges user is NOT eligible for. | Low |
| **P1-27** | `tools/pdf_retriever.py` | 74 | `retrieve_chunks` adds `_text_lower`, `_token_count` keys to input chunk dicts **in-place**. Caller's chunks mutated. | Side effects; bugs if chunks reused. | Low |
| **P1-28** | `pipelines/general_pipeline.py` | 95 | `run_agents` called without `complexity_override` for explanatory queries — re-detects complexity redundantly. | May use different level than initial detection. | Low |
| **P1-29** | `backend/services/pipeline_dispatcher.py` | 53–62 | Fallback to `general_pipeline` on any pipeline failure. `general_pipeline` calls `run_agents` → may recurse back to dispatcher if agent chain fails. | Stack overflow on cascading failures. | Medium |
| **P1-30** | `backend/services/streaming_service.py` | 8–18 | `stream_text_chunks` yields 256-byte chunks, splitting **mid-word/character**. | Frontend receives partial words; ugly rendering. | Low |
| **P1-31** | `llm/ollama_client.py` | 85–90 | `cached_llm_call` cache key is `(prompt, system, num_predict, temperature)` — **model name not included**. | Changing `OLLAMA_MODEL` at runtime returns stale cached responses. | Low |

---

## 4. P2 — Technical Debt & Performance

| # | File | Line(s) | Issue | Impact | Fix Complexity |
|---|------|---------|-------|--------|----------------|
| **P2-01** | `backend/services/chatbot_service.py` | 73 | Bare `except Exception:` without `raise ... from exc` chaining. | Traceback context lost in FastAPI error responses. | Low |
| **P2-02** | `backend/services/pipeline_dispatcher.py` | 45, 53 | Same as P2-01 — bare except loses traceback. | Harder debugging. | Low |
| **P2-03** | `backend/services/pdf_service.py` | 19, 35, 47 | Same as P2-01. | Harder debugging. | Low |
| **P2-04** | `pipelines/coding_pipeline.py` | 196 | Same as P2-01 — bare except in pipeline. | Harder debugging. | Low |
| **P2-05** | `pipelines/education_pipeline.py` | 85 | Same as P2-01. | Harder debugging. | Low |
| **P2-06** | `pipelines/general_pipeline.py` | 82 | Same as P2-01. | Harder debugging. | Low |
| **P2-07** | `pipelines/medical_pipeline.py` | 123 | Same as P2-01. | Harder debugging. | Low |
| **P2-08** | `agents/llm_agents.py` | 28–33 | `_estimate_confidence` purely length-based: <50=0.7, 100-300=0.95, >500=0.75. No semantic basis. | Policy decisions (expert/refiner) based on meaningless metric. | Medium |
| **P2-09** | `llm/ollama_client.py` | 38 | `_SESSION` global `requests.Session` — not closed on shutdown. | Socket leak in long-running processes. | Low |
| **P2-10** | `tools/pdf_store.py` | 45–65 | `load()` acquires lock, calls CPU-intensive `extract_pages()` and `chunk_pages()` (seconds) under lock. | All other PDF operations blocked during parse; latency spikes. | Medium |
| **P2-11** | `router/domain_router.py` | 45–250 | `_EDUCATION_KW` dict with ~300 entries inlined. Unmaintainable. | Typos risk; no external config. | Medium |
| **P2-12** | `utils/complexity.py` | 8–45 | `_HIGH_KEYWORDS`, `_MEDIUM_KEYWORDS`, `_LOW_KEYWORDS` hardcoded frozensets. No env override. | Tuning requires code change. | Low |
| **P2-13** | `utils/section_parser.py` | 35–50 | `@cache` key is tuple of (canonical, tuple(aliases)) — **order-dependent**. Dict insertion order changes → cache miss. | Reduced cache effectiveness. | Low |
| **P2-14** | `tools/college_predictor.py` | 14 | `load_data()` returns full pandas DataFrame (~100k rows) kept in memory globally. | Memory usage ~50-100MB; acceptable but not scalable. | Low |
| **P2-15** | `backend/services/chat_history.py` | 55, 105, 125 | `_persist()` writes entire user chat history to disk on every create/append/delete. No batching, no async I/O. | Latency on chat ops; disk wear. | Medium |
| **P2-16** | `backend/auth/user_store.py` | 45–55 | `_save()` writes JSON. Lock is **per-process** — under gunicorn multi-worker, race condition corrupts file. | User data corruption in production. | High |
| **P2-17** | `tools/pdf_retriever.py` | 65–75 | Same as P1-27 — side effect noted here for debt tracking. | Unexpected mutation of shared state. | Low |
| **P2-18** | `utils/text_cleaner.py` | 15–20 | `_FILLER_RE` hardcoded list misses many LLM fillers: "Here is", "Here's", "I'll explain", "Let me". | Verbose responses not fully cleaned. | Low |
| **P2-19** | `backend/services/streaming_service.py` | 8–18 | Same as P1-30 — yields 256-byte chunks splitting mid-word. | Bad frontend rendering. | Low |
| **P2-20** | `utils/agent_executor.py` | 38 | `_cached_base_result` caches by query string only. Same query with different chat history returns stale answer. | Incorrect cached responses in conversations. | Medium |
| **P2-21** | `utils/response_formatter.py` | 1–30 | Header says "BACKWARD COMPATIBILITY LAYER — Will eventually disappear" but `formatter_dispatcher.py` still calls it. | Dead code path maintained; confusion. | Medium |
| **P2-22** | Multiple | — | Magic numbers scattered: token expiry 30/7, cookie max_age `30*60`/`7*24*60*60`, token caps 400/550/800, thresholds 20/10000/3000. | Tuning requires code changes; inconsistency. | Medium |
| **P2-23** | `schemas/education_schema.py` | — | Labels use `"📖 Definition"` with emojis; pipeline `_SECTION_LABELS` uses `"DEFINITION"` (plain). | Formatter expects emojis; pipeline emits plain → parsing fails. | Medium |
| **P2-24** | `pipelines/pipeline_result.py` | 25–27 | `data: PipelineData = None` — no validation that data matches domain. | Type confusion; wrong model for domain. | Medium |
| **P2-25** | `agents/llm_agents.py` | 14 | `run_base_agent` hardcodes `num_predict=250`. Doesn't adapt to query complexity. | Low-complexity queries waste tokens. | Low |
| **P2-26** | `agents/agent_policy.py` | 24 | Thresholds `_MIN_CONFIDENCE_FOR_EXPERT=0.6`, etc. — magic numbers, not configurable. | Cannot tune behavior without code change. | Low |
| **P2-27** | `llm/ollama_client.py` | 133 | `_parse_ollama_response` handles NDJSON fallback but `call_llm` always uses `stream: false`. | NDJSON path is dead code. | Low |
| **P2-28** | `utils/cache.py` | 10 | `cached_llm_call` and `cached_response` both use `lru_cache` with maxsize=256 — caches LLM responses by exact prompt; memory grows unbounded for varied queries. | Memory pressure under diverse query load. | Low |
| **P2-29** | `utils/complexity.py` | 21 | `_HIGH_KEYWORDS` includes `"create a"` but not `"create"` — `"create database"` → low; `"create a database"` → high. | Inconsistent complexity detection. | Low |
| **P2-30** | `tools/pdf_session_manager.py` | 68 | `get_store` calls `_cleanup_if_needed` on every access — scans all sessions O(n) per request. | Latency linear with session count. | Low |
| **P2-31** | `router/domain_router.py` | 434 | `_EDUCATION_KW` built from `_Y1`..`_Y4` via `**` merge — later years overwrite earlier for duplicate keys. | Keyword weights may be silently wrong. | Low |
| **P2-32** | `pipelines/coding_pipeline.py` | 44 | `_CODE_PATTERN` defined but only used in `coding_pipeline()` — not in `_clean_code_output`. Duplicate logic. | Maintenance burden. | Low |
| **P2-33** | `pipelines/education_pipeline.py` | 29 | `_TOKEN_CAP` uses `final` type hint instead of `Final` from `typing`. | Inconsistent with codebase conventions. | Low |
| **P2-34** | `pipelines/medical_pipeline.py` | 55 | `_HIGH_RISK_PATTERNS` mixes tuples and strings — `isinstance` check handles both but fragile. | Maintenance risk. | Low |
| **P2-35** | `llm/ollama_client.py` | 85 | `MAX_RETRIES = 1` but loop runs `MAX_RETRIES + 2` times (3 attempts). Confusing naming. | Misleading constant name. | Low |
| **P2-36** | `frontend/src/routes.jsx` | 7–22 | `RequireAuth` defined inline in `routes.jsx`. Not reusable. | Duplication risk if auth guard needed elsewhere. | Low |
| **P2-37** | `frontend/src/components/ChatWindow.jsx` | 31–49 | `quickPrompts` hardcoded in component. | Not configurable. | Low |
| **P2-38** | `frontend/src/pages/ChatPage.jsx` | 13 | `chats` from store not in effect deps; filtered chats recomputed on every render. | Minor perf issue. | Low |
| **P2-39** | `agents/models.py` | 18 | `AgentResult.__post_init__` validates confidence 0–1 and tokens ≥ 0; `_estimate_tokens` can return 0 for empty string. | Edge case but valid. | Low |
| **P2-40** | `tools/pdf_store.py` | 56 | `load()` catches `Exception`, calls `self.clear()`, then `raise`. `clear()` acquires same lock — potential deadlock if exception during lock hold. | Deadlock risk on parse failure. | Low |
| **P2-41** | `config/college_config.py` | 10–13 | `int(__import__("os").getenv(...))` — awkward pattern. | Hard to read. | Low |
| **P2-42** | `config/__init__.py` | 3–5 | Uses `from .llm_config import *` etc. — hides config sources. | Hard to trace where constants come from. | Low |

---

## 5. P3 — Cleanup & Dead Code

| # | File | Line(s) | Issue | Impact | Fix Complexity |
|---|------|---------|-------|--------|----------------|
| **P3-01** | `backend/api/routes/auth.py` | 3 | Unused import `Response`. | Lint noise. | Low |
| **P3-02** | `backend/api/routes/chat.py` | 1 | Unused import `os`. | Lint noise. | Low |
| **P3-03** | `backend/api/routes/coding.py` | — | Unused `GENERAL_DOMAIN` import. | Lint noise. | Low |
| **P3-04** | `backend/api/routes/college.py` | — | Unused `GENERAL_DOMAIN` import. | Lint noise. | Low |
| **P3-05** | `backend/api/routes/education.py` | — | Unused `GENERAL_DOMAIN` import. | Lint noise. | Low |
| **P3-06** | `backend/api/routes/medical.py` | — | Unused `GENERAL_DOMAIN` import. | Lint noise. | Low |
| **P3-07** | `tools/pdf_to_json.py` | — | Not imported anywhere. Legacy conversion script. | Clutter. | Low |
| **P3-08** | `schemas/college_schema.py` | — | Empty module (docstring only) after prior cleanup. | Dead code. | Low |
| **P3-09** | `schemas/__init__.py` | — | Docstring references `general_schema` which doesn't exist. | Misleading docs. | Low |
| **P3-10** | `constants/__init__.py` | — | Only exports `DIVIDER`; `domains.py` not re-exported. | Inconsistent. | Low |
| **P3-11** | `backend/models/__init__.py` | — | `from .response_models import *` — namespace pollution. | Unclear public API. | Low |
| **P3-12** | `utils/__init__.py` | — | Missing — not a proper Python package. | Minor. | Low |
| **P3-13** | `tools/__init__.py` | — | Missing — not a proper Python package. | Minor. | Low |
| **P3-14** | `backend/services/__init__.py` | — | Empty. | Minor. | Low |
| **P3-15** | `backend/api/routes/__init__.py` | — | Empty. | Minor. | Low |
| **P3-16** | `backend/auth/__init__.py` | — | Empty. | Minor. | Low |
| **P3-17** | `app.py` | 42–53 | `_warmup()` loads dataset; `backend/main.py` lifespan also loads. Double load if both entry points run. | Wasteful. | Low |
| **P3-18** | `frontend/src/index.css` | 79 | Duplicate `@keyframes fadeUp` (also at line ~1140). | Redundancy. | Low |
| **P3-19** | `frontend/src/index.css` | 85–87 | Duplicate `@keyframes fadeIn`. | Redundancy. | Low |
| **P3-20** | `frontend/src/index.css` | 91–93 | Duplicate `@keyframes slideIn`. | Redundancy. | Low |
| **P3-21** | `frontend/src/index.css` | 97–100 | Duplicate `@keyframes typingBounce`. | Redundancy. | Low |
| **P3-22** | `frontend/src/index.css` | 194 | `.chat-item` has `group: true` — invalid CSS property (Tailwind syntax in plain CSS). | Lint error. | Low |
| **P3-23** | `frontend/src/index.css` | 763 | `.code-header` defined twice with different styles. | Unpredictable cascade. | Low |
| **P3-24** | `frontend/src/index.css` | — | `--accent-green`, `--accent-college`, `--brand-from` used but never defined in `:root`. | Undefined CSS custom properties. | Low |
| **P3-25** | `frontend/src/services/authService.js` | 33–37 | `refreshToken` defined but never called. | Dead code. | Low |
| **P3-26** | `frontend/src/services/authStorage.js` | 34–36 | `getStoredToken` defined but never used. | Dead code. | Low |
| **P3-27** | `frontend/src/store/pdfStore.js` | 31 | `uploadPdf` accepts `sessionId` but never passed from ChatPage. | Unused param. | Low |
| **P3-28** | `tests/` | — | Massive coverage gaps: no pipeline tests, no router tests, no extractor tests, no college predictor tests, no config tests, no integration tests. | Low confidence in refactors. | High |

---

## 6. Summary & Recommended Order

### Fix Priority Matrix

| Week | Priority | Issues | Theme |
|------|----------|--------|-------|
| **Week 1** | P0 | P0-01 to P0-06, P0-08 to P0-10, P0-12 | Stop crashes, fix security surface |
| **Week 1** | P0 | P0-15, P0-16, P0-18 | Fix frontend security & broken upload |
| **Week 2** | P1 | P1-03, P1-12, P1-26, P1-29 | Fix broken contracts & logic |
| **Week 2** | P1 | P1-18, P1-19, P1-22 | Fix agent/expert policy & async |
| **Week 3** | P2 | P2-10, P2-14, P2-15, P2-16, P2-22 | Performance & reliability |
| **Week 3** | P2 | P2-21, P2-23, P2-24 | Complete PipelineResult migration |
| **Week 4** | P3 | P3-01 to P3-06, P3-18 to P3-27 | Dead code & CSS cleanup |
| **Sprint N** | P3 | P3-28 | Write comprehensive test suite |

### Critical Paths

1. **Sync blocking in async app** (P0-02 through P0-06) is the single biggest production risk. A single slow LLM request hangs the entire server.
2. **localStorage tokens** (P0-15) + **broken multipart upload** (P0-16) break the frontend/auth flow.
3. **Inverted cutoff logic** (P1-26) means the college predictor returns the *opposite* of eligible colleges — a severe functional defect.
4. **JWT single key** (P0-07) + **hardcoded admin** (P0-12) are security landmines for any production deployment.
5. **Keypoints/key_points mismatch** (P0-19) silently breaks education data formatting.

---

## 7. Architectural Dependency Graph

```
User Query
│
├─► React (ChatPage.jsx)
│   ├─► chatStore.js ──► chatService.js ──► apiService.js (Axios)
│   └─► pdfStore.js ──► pdfService.js
│
├─► Axios POST /chat (or domain routes)
│
├─► FastAPI Route (backend/api/routes/*.py)
│   ├─► Auth Dependency ──► jwt_service.py
│   ├─► Pydantic Models ──► response_models.py
│   └─► chatbot_service.process_query()
│
├─► chatbot_service.py
│   ├─► domain_router.py (keyword scoring)
│   ├─► pipeline_dispatcher.py
│   │   ├─► college_pipeline.py ──► college_predictor.py
│   │   ├─► coding_pipeline.py ──► call_llm()
│   │   ├─► education_pipeline.py ──► call_llm()
│   │   ├─► medical_pipeline.py ──► call_llm()
│   │   ├─► pdf_pipeline.py ──► pdf_store / pdf_retriever
│   │   └─► general_pipeline.py ──► agent_executor.py
│   │       ├─► base_agent ──► call_llm()
│   │       ├─► refiner_agent ──► call_llm()
│   │       └─► expert_agent ──► call_llm()
│   └─► formatter_dispatcher.py
│       ├─► PipelineResult.data (structured)
│       └─► response_formatter.py (legacy string parsing)
│
├─► call_llm() ──► requests.Session().post() ──► Ollama API
│   └─► Synchronous, blocks ASGI loop
│
└─► Response flows back through formatter → ChatResponse → JSONResponse
```

### Key Architectural Boundary Violations

| Violation | From | To | Impact |
|-----------|------|-----|--------|
| Service → Agent | `formatter_dispatcher.py` | `agents/extractor_agent.py` | Service layer should not depend on agents |
| Store → Store | `chatStore.js` | `pdfStore.getState()` | Cross-store coupling |
| Dual API Clients | `apiService.js` | `authService.js` | Competing Axios instances, divergent interceptors |
| Sync LLM in Async App | FastAPI endpoints | `ollama_client.call_llm` | Blocks event loop for 5–240s |
| Broken formatter contract | `education_pipeline.py` | `EDUCATION_LABELS` | `"keypoints"` vs `"key_points"` |
| Inverted predictor logic | `college_predictor.py` | DataFrame filter | Returns wrong colleges |

---

*End of Audit Report V2*
