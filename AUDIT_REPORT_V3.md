# AUDIT_REPORT_V3.md — Repository Architecture Audit

**Scope:** Complete repository audit of `backend/`, `frontend/`, `agents/`, `pipelines/`, `router/`, `llm/`, `utils/`, `tools/`, `schemas/`, `constants/`, `config/`, `tests/`
**Date:** 2026-06-22
**Auditor:** kimchi-agent
**Files examined:** 90+ modules

---

## P0 — CRITICAL / SECURITY / EXPLOITABLE

### P0-01 — JWT secret keys resolve to `None` when env vars are unset
- **Severity:** P0
- **Affected Files:** `backend/auth/jwt_service.py:18-19`
- **Impact:** `_ACCESS_SECRET_KEY` and `_REFRESH_SECRET_KEY` are `None` if env vars are unset. The deferred `_ensure_secrets()` raises at first use, but `SECRET_KEY` alias and any import-time references get `None` silently. Token creation can fail with obscure errors.
- **Recommended Fix:** Validate secrets during FastAPI startup rather than per-request. Add `assert key is not None` before passing to PyJWT.
- **Fix Complexity:** Low
- **Groupable:** Yes (jwt_service group)

### P0-02 — `decode_token` passes `None` key when `_ACCESS_SECRET_KEY` is unset
- **Severity:** P0
- **Affected Files:** `backend/auth/jwt_service.py:72-84`
- **Impact:** When `expected_type=None` or `"access"`, `decode_token` uses `_ACCESS_SECRET_KEY`. If this is `None`, PyJWT receives `None` and raises confusing `InvalidTokenError`.
- **Recommended Fix:** Assert key is not None after `_ensure_secrets()` call.
- **Fix Complexity:** Low
- **Groupable:** Yes (jwt_service group)

### P0-03 — No file size limit on PDF upload — DoS vector
- **Severity:** P0
- **Affected Files:** `backend/api/routes/pdf.py:139-141`, `backend/main.py`
- **Impact:** `await file.read()` loads entire body into memory. No global request size limit configured. Arbitrary file uploads exhaust disk/memory.
- **Recommended Fix:** Add request body size limit via Starlette middleware. Stream in chunks with explicit max size check.
- **Fix Complexity:** Medium
- **Groupable:** Independent

### P0-04 — Cookie `secure` flag defaults to `False` — breaks HTTPS auth
- **Severity:** P0
- **Affected Files:** `backend/api/routes/auth.py:15`, `40,48,139,147`
- **Impact:** In production behind HTTPS, `secure=False` cookies are silently rejected by browsers. Users login successfully but subsequent requests fail auth.
- **Recommended Fix:** Default to `True`; use `COOKIE_INSECURE=true` override for dev.
- **Fix Complexity:** Low
- **Groupable:** Yes (auth.py cookie group)

### P0-05 — No rate limiting on auth endpoints — brute-force exposure
- **Severity:** P0
- **Affected Files:** `backend/api/routes/auth.py:22-165`
- **Impact:** Unlimited login/register/refresh attempts. Credential stuffing possible at scale.
- **Recommended Fix:** Add `slowapi` or custom rate limiting. Track failed attempts, lock accounts after N failures.
- **Fix Complexity:** Medium
- **Groupable:** Yes (auth security group)

### P0-06 — Singletons initialized at import time — startup coupling & test isolation
- **Severity:** P0
- **Affected Files:** `backend/auth/user_store.py:80`, `backend/services/chat_history.py:124`
- **Impact:** `user_store = UserStore()` and `chat_history_manager = ChatHistoryManager()` block startup, read disk at import, and cause test isolation issues. `os.makedirs` in `__init__` can fail with permission errors.
- **Recommended Fix:** Use FastAPI `Depends` factories or `lru_cache` factories. Move directory creation to app startup.
- **Fix Complexity:** Medium
- **Groupable:** Yes (singleton group)

### P0-07 — UserStore read paths have no lock — RuntimeError on concurrent writes
- **Severity:** P0
- **Affected Files:** `backend/auth/user_store.py:51-57, 74-76`
- **Impact:** `get_user`, `get_user_by_email`, `username_exists` read without lock. Concurrent `create_user` can cause `dictionary changed size during iteration`.
- **Recommended Fix:** Acquire lock in read methods or copy dict for reads.
- **Fix Complexity:** Low
- **Groupable:** Yes (user_store group)

### P0-08 — ChatHistoryManager._persist silently swallows disk failures
- **Severity:** P0
- **Affected Files:** `backend/services/chat_history.py:36-42`
- **Impact:** Catches all `OSError` silently. If disk is full, data accepted in memory but lost on restart. Users get 200 but data is gone.
- **Recommended Fix:** Log ERROR. Raise custom exception for route to return 500.
- **Fix Complexity:** Low
- **Groupable:** Yes (chat_history group)

### P0-09 — data_loader.py global mutable state has no lock — thundering herd
- **Severity:** P0
- **Affected Files:** `tools/data_loader.py:29, 48-56`
- **Impact:** Check-then-act race on `_df`. Multiple workers load CSV simultaneously.
- **Recommended Fix:** Wrap in `threading.Lock()`.
- **Fix Complexity:** Low
- **Groupable:** Yes (tools concurrency group)

### P0-10 — Frontend/backend data model mismatch — structured responses broken
- **Severity:** P0
- **Affected Files:** `frontend/src/components/CodingResponse.jsx:11-20`, `AcademicResponse.jsx:9-20`, `MedicalResponse.jsx:9-17` vs `backend/models/response_models.py:20-50`
- **Impact:** Frontend expects `time_complexity`, `key_formulas`, `possible_causes` but backend returns `complexity`, `key_points`, `conditions`. Structured responses show empty defaults.
- **Recommended Fix:** Align frontend destructuring with backend fields or create a response mapper.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend model group)

### P0-11 — 12 JWT tests fail — env var not set before first use
- **Severity:** P0
- **Affected Files:** `tests/test_jwt_service.py:53-136`
- **Impact:** `create_access_token` calls `_ensure_secrets()` which raises if `JWT_SECRET_KEY` is not set. Test classes import at module level without env setup.
- **Recommended Fix:** Add autouse fixture setting `JWT_SECRET_KEY` for JWT tests.
- **Fix Complexity:** Low
- **Groupable:** Yes (test infrastructure group)

---

## P1 — HIGH / SECURITY / RUNTIME BUGS

### P1-01 — Missing input length validation on all chat request models
- **Severity:** P1
- **Affected Files:** `backend/models/request_models.py:9-14`, `37-43`
- **Impact:** Only `min_length=1`, no max. 1MB messages can DOS Ollama and exhaust memory.
- **Recommended Fix:** Add `max_length=8000` (configurable).
- **Fix Complexity:** Low
- **Groupable:** Yes (request model group)

### P1-02 — username_exists case-sensitive vs get_user normalized
- **Severity:** P1
- **Affected Files:** `backend/auth/user_store.py:51-53, 74-76`
- **Impact:** Mismatch allows case-variation duplicates.
- **Recommended Fix:** Normalize in `username_exists`.
- **Fix Complexity:** Low
- **Groupable:** Yes (user_store group)

### P1-03 — No password complexity requirements
- **Severity:** P1
- **Affected Files:** `backend/models/request_models.py:40`, `backend/auth/password_utils.py:7-9`
- **Impact:** Any 6-char string accepted, including all spaces.
- **Recommended Fix:** Add Pydantic validator requiring 1 letter + 1 digit.
- **Fix Complexity:** Low
- **Groupable:** Yes (auth security group)

### P1-04 — ChatHistoryManager uses deprecated `datetime.utcnow()`
- **Severity:** P1
- **Affected Files:** `backend/services/chat_history.py:46`
- **Impact:** Deprecated in Python 3.12+. Returns naive datetime.
- **Recommended Fix:** Use `datetime.now(timezone.utc)`.
- **Fix Complexity:** Low
- **Groupable:** Yes (chat_history group)

### P1-05 — ollama_client retry loop bound bug
- **Severity:** P1
- **Affected Files:** `llm/ollama_client.py:57`
- **Impact:** `range(1, MAX_RETRIES + 2)` creates off-by-one. HTTP errors break immediately without retry.
- **Recommended Fix:** Use `range(1, MAX_RETRIES + 1)` and remove premature break statements.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P1-06 — pdf_to_json hardcoded paths and runs at import
- **Severity:** P1
- **Affected Files:** `tools/pdf_to_json.py:9-18`
- **Impact:** Module-level path computation happens at import. Case-sensitive filename mismatch likely.
- **Recommended Fix:** Use env vars for paths. Move computation inside `if __name__ == "__main__"`.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P1-07 — detect_cycles.py — import side effect risk
- **Severity:** P1
- **Affected Files:** `tools/detect_cycles.py`
- **Impact:** Standalone script inside `tools/` package. If imported, `main()` could be executed accidentally.
- **Recommended Fix:** Move to `scripts/` or `devtools/` directory.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P1-08 — process_query has no input length guard
- **Severity:** P1
- **Affected Files:** `backend/services/chatbot_service.py:41-42`
- **Impact:** 1MB messages flow through pipeline unchallenged.
- **Recommended Fix:** Truncate or reject messages > 5000 chars at entry.
- **Fix Complexity:** Low
- **Groupable:** Yes (chatbot_service group)

### P1-09 — No CSRF token mechanism despite withCredentials
- **Severity:** P1
- **Affected Files:** `frontend/src/services/apiService.js:7,13`, `backend/api/routes/auth.py`
- **Impact:** `withCredentials: true` but no CSRF token. SameSite provides some protection but not complete.
- **Recommended Fix:** Implement CSRF tokens for state-changing endpoints.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend security group)

### P1-10 — Frontend stores user profile in localStorage unencrypted
- **Severity:** P1
- **Affected Files:** `frontend/src/store/authStore.js:15-20`, `frontend/src/services/authStorage.js`
- **Impact:** User profile data vulnerable to XSS theft even though tokens are in httpOnly cookies.
- **Recommended Fix:** Store only user ID in localStorage; fetch profile from API. Or encrypt data.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend security group)

### P1-11 — UserStore stores bcrypt hashes in plain JSON — no encryption at rest
- **Severity:** P1
- **Affected Files:** `backend/auth/user_store.py:49`
- **Impact:** `users.json` contains password hashes readable by anyone with filesystem access. Offline cracking possible.
- **Recommended Fix:** Encrypt file at rest with Fernet or migrate to SQLite/PostgreSQL.
- **Fix Complexity:** High
- **Groupable:** Independent

### P1-12 — Refresh token rotation breaks concurrent sessions
- **Severity:** P1
- **Affected Files:** `backend/api/routes/auth.py:103-158`
- **Impact:** Every refresh issues new token. Multi-tab users get logged out unexpectedly.
- **Recommended Fix:** Implement refresh token reuse detection with token families.
- **Fix Complexity:** High
- **Groupable:** Yes (auth security group)

### P1-13 — domain_router lru_cache on long strings — unbounded cache keys
- **Severity:** P1
- **Affected Files:** `router/domain_router.py:219-225`
- **Impact:** No input length guard before caching. Maliciously long queries bloat cache memory.
- **Recommended Fix:** Reject or truncate queries > 1000 chars before caching.
- **Fix Complexity:** Low
- **Groupable:** Independent

---

## P2 — MEDIUM / RUNTIME / MAINTAINABILITY

### P2-01 — Streaming service loads full response into memory before chunking
- **Severity:** P2
- **Affected Files:** `backend/services/streaming_service.py:7-20`
- **Impact:** `text.encode("utf-8")` allocates full response. Combined with P0-03 (no input limit), can exhaust memory.
- **Recommended Fix:** Add max_length validation on MessageRequest. Make chunking configurable.
- **Fix Complexity:** Medium
- **Groupable:** Yes (memory management group)

### P2-02 — PDF upload doubles memory — reads full file into memory
- **Severity:** P2
- **Affected Files:** `backend/api/routes/pdf.py:139-141`
- **Impact:** `await file.read()` then `file_obj.write(content)` uses 2x file size memory.
- **Recommended Fix:** Stream in chunks: `while chunk := await file.read(65536): file_obj.write(chunk)`.
- **Fix Complexity:** Low
- **Groupable:** Yes (pdf upload group)

### P2-03 — load_pdf_by_path returns 200 for missing files instead of 404
- **Severity:** P2
- **Affected Files:** `backend/api/routes/pdf.py:56-102`
- **Impact:** Missing files return `success=False` with HTTP 200. Broken API contract.
- **Recommended Fix:** Check `os.path.exists()` before `load_pdf`; raise `HTTPException(404)`.
- **Fix Complexity:** Low
- **Groupable:** Yes (pdf route group)

### P2-04 — Sync auth routes in async-first FastAPI app
- **Severity:** P2
- **Affected Files:** `backend/api/routes/auth.py:22,64,103,163`
- **Impact:** bcrypt hashing blocks thread pool thread. Under load, thread pool exhaustion stalls requests.
- **Recommended Fix:** Convert to `async def` and wrap bcrypt with `asyncio.to_thread()`.
- **Fix Complexity:** Low
- **Groupable:** Yes (auth route group)

### P2-05 — Domain routes are copy-paste duplicates — DRY violation
- **Severity:** P2
- **Affected Files:** `backend/api/routes/education.py`, `coding.py`, `medical.py`, `college.py`
- **Impact:** Identical implementation. Changes must be made in 4 places.
- **Recommended Fix:** Create generic domain handler and import per route.
- **Fix Complexity:** Low
- **Groupable:** Yes (route refactoring group)

### P2-06 — No pagination on GET /chats
- **Severity:** P2
- **Affected Files:** `backend/api/routes/chat.py:29-31`
- **Impact:** Returns all chats in one request. Large users get huge responses.
- **Recommended Fix:** Add `skip` and `limit` query params.
- **Fix Complexity:** Low
- **Groupable:** Yes (chat route group)

### P2-07 — ChatRequest missing domain field vs ChatMessageRequest has domain
- **Severity:** P2
- **Affected Files:** `backend/models/request_models.py:16-19` vs `31-34`
- **Impact:** Inconsistent models. Client cannot hint domain for chat routing.
- **Recommended Fix:** Add `domain: str | None = None` to ChatRequest.
- **Fix Complexity:** Low
- **Groupable:** Yes (model consistency group)

### P2-08 — _format_chat_detail silently drops unexpected fields
- **Severity:** P2
- **Affected Files:** `backend/api/routes/chat.py:22-25`
- **Impact:** Manual dict filtering drops unknown fields silently.
- **Recommended Fix:** Use `model_validate` or whitelist with warning logs.
- **Fix Complexity:** Low
- **Groupable:** Yes (chat route group)

### P2-09 — ChatMessageRequest.sender unvalidated — fake system messages possible
- **Severity:** P2
- **Affected Files:** `backend/models/request_models.py:31-34`
- **Impact:** Any sender string accepted, including "admin" or "system".
- **Recommended Fix:** Restrict to `Literal["user", "bot"]`.
- **Fix Complexity:** Low
- **Groupable:** Yes (model validation group)

### P2-10 — chat_history_manager persists entire store on every message
- **Severity:** P2
- **Affected Files:** `backend/services/chat_history.py:96-126`
- **Impact:** Every write serializes full JSON. Contention on lock, performance bottleneck.
- **Recommended Fix:** Write-behind cache or write only modified chat.
- **Fix Complexity:** High
- **Groupable:** Yes (chat_history group)

### P2-11 — empty string return from ollama_client on all failures
- **Severity:** P2
- **Affected Files:** `llm/ollama_client.py:76-79`
- **Impact:** Returns "" on failure. Callers show placeholder or nothing. Silent degradation.
- **Recommended Fix:** Raise `RuntimeError` so callers handle consistently.
- **Fix Complexity:** Low
- **Groupable:** Yes (ollama_client group)

### P2-12 — pdf_pipeline returns str instead of PipelineResult
- **Severity:** P2
- **Affected Files:** `pipelines/pdf_pipeline.py:67-77`, `backend/services/chatbot_service.py:34-36`
- **Impact:** Only pipeline returning string. Bypasses structured formatter.
- **Recommended Fix:** Migrate to return PipelineResult.
- **Fix Complexity:** Medium
- **Groupable:** Yes (pipeline architecture group)

### P2-13 — Redundant double-parse in medical, education, coding pipelines
- **Severity:** P2
- **Affected Files:** `pipelines/medical_pipeline.py:173-183`, `education_pipeline.py:95-128`, `coding_pipeline.py:158-171`
- **Impact:** Parse raw response, format it, then re-parse formatted output. Wasted CPU.
- **Recommended Fix:** Use already-parsed variables directly to construct data models.
- **Fix Complexity:** Low
- **Groupable:** Yes (pipeline efficiency group)

### P2-14 — formatter_dispatcher _format is dead code
- **Severity:** P2
- **Affected Files:** `backend/services/formatter_dispatcher.py:27-29,55-63`
- **Impact:** `_format` and its `else` branch in `dispatch_formatter` are unreachable. All pipelines return PipelineResult.
- **Recommended Fix:** Remove dead code.
- **Fix Complexity:** Low
- **Groupable:** Yes (formatter group)

### P2-15 — agent_policy _MIN_CONFIDENCE_FOR_EXPERT naming inverted
- **Severity:** P2
- **Affected Files:** `agents/agent_policy.py:38-43`
- **Impact:** Variable name says "minimum for expert" but logic skips expert when confidence is HIGH. Misleading.
- **Recommended Fix:** Rename to `_MAX_CONFIDENCE_TO_SKIP_EXPERT`.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P2-16 — llm_agents token estimation by char count is inaccurate
- **Severity:** P2
- **Affected Files:** `agents/llm_agents.py:39-43`
- **Impact:** 0.25 factor is rough heuristic. Policy decisions based on wrong token counts.
- **Recommended Fix:** Use `tiktoken` or safer 0.2 factor.
- **Fix Complexity:** Medium
- **Groupable:** Yes (agent group)

### P2-17 — medical_pipeline safety filter only covers 9 specific drugs
- **Severity:** P2
- **Affected Files:** `pipelines/medical_pipeline.py:44-54`
- **Impact:** Incomplete coverage. Drug classes, brand names, dosages not filtered.
- **Recommended Fix:** Expand list to classes and interactions.
- **Fix Complexity:** Low
- **Groupable:** Yes (medical pipeline group)

### P2-18 — pdf_retriever mutates shared chunk dict without lock
- **Severity:** P2
- **Affected Files:** `tools/pdf_retriever.py:73-77`
- **Impact:** Adds cache keys to shared chunk dicts. Race condition under concurrent queries.
- **Recommended Fix:** Use separate cache dict keyed by chunk_id or add lock.
- **Fix Complexity:** Medium
- **Groupable:** Yes (tools concurrency group)

### P2-19 — requests.Session module-level — thread safety concerns
- **Severity:** P2
- **Affected Files:** `llm/ollama_client.py:39`
- **Impact:** Module-level session shared across threads. Connection state may be modified concurrently.
- **Recommended Fix:** Use per-call session or `urllib3.PoolManager`.
- **Fix Complexity:** Medium
- **Groupable:** Yes (ollama_client group)

### P2-20 — pdf_session_store.py is a pointless re-export shim
- **Severity:** P2
- **Affected Files:** `tools/pdf_session_store.py`
- **Impact:** 2-line alias module. Adds indirection for no benefit.
- **Recommended Fix:** Remove if unused; update imports to use pdf_session_manager.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P2-21 — pdf_reader silently skips image-only pages
- **Severity:** P2
- **Affected Files:** `tools/pdf_reader.py:58-62`
- **Impact:** Scanned PDFs return empty page list with no error.
- **Recommended Fix:** If pages list is empty after extraction, raise descriptive error.
- **Fix Complexity:** Low
- **Groupable:** Yes (pdf tools group)

### P2-22 — No domain pre-validation on specialized endpoints
- **Severity:** P2
- **Affected Files:** `backend/api/routes/chat.py`, `college.py`, `medical.py`, `coding.py`, `education.py`
- **Impact:** Calling `/medical` with a college query works (routes to general domain). Breaks API contract.
- **Recommended Fix:** Fast pre-classify before LLM call. Return 400 if mismatch.
- **Fix Complexity:** Medium
- **Groupable:** Yes (route contract group)

### P2-23 — college_pipeline iterates DataFrames with iterrows (slow)
- **Severity:** P2
- **Affected Files:** `pipelines/college_pipeline.py:57-89`
- **Impact:** `iterrows()` is notoriously slow pandas operation.
- **Recommended Fix:** Use vectorized string formatting or `apply`.
- **Fix Complexity:** Low-Medium
- **Groupable:** Yes (college pipeline group)

### P2-24 — schemas label fragmentation — two label sets per domain
- **Severity:** P2
- **Affected Files:** `schemas/medical_schema.py`, `education_schema.py`, `coding_schema.py` vs pipeline internal labels
- **Impact:** Pipelines use `_SECTION_LABELS` (no emoji); schemas use `*_LABELS` (with emoji). Fragile matching.
- **Recommended Fix:** Unify label sets.
- **Fix Complexity:** Low
- **Groupable:** Yes (schema alignment group)

### P2-25 — No logging in domain route handlers
- **Severity:** P2
- **Affected Files:** `backend/api/routes/coding.py`, `medical.py`, `college.py`, `education.py`
- **Impact:** No visibility in production.
- **Recommended Fix:** Add structured logging.
- **Fix Complexity:** Low
- **Groupable:** Yes (logging group)

### P2-26 — frontend chatStore mixes concerns with pdfStore
- **Severity:** P2
- **Affected Files:** `frontend/src/store/chatStore.js:3,88,91`
- **Impact:** ChatStore imports from PDFStore directly. Violates separation.
- **Recommended Fix:** Pass pdf status as parameter or use shared context.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend store group)

### P2-27 — frontend race condition in chat submission
- **Severity:** P2
- **Affected Files:** `frontend/src/store/chatStore.js:85-131`
- **Impact:** No guard prevents submit during loading. Duplicate messages possible.
- **Recommended Fix:** Guard on isLoading. Disable send button during loading.
- **Fix Complexity:** Low
- **Groupable:** Yes (frontend async group)

### P2-28 — frontend no request cancellation on unmount
- **Severity:** P2
- **Affected Files:** `frontend/src/store/chatStore.js:45-54,85-131`
- **Impact:** Requests continue after component unmount. State updates on unmounted components.
- **Recommended Fix:** Use AbortController and cleanup in useEffect.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend async group)

### P2-29 — frontend duplicate getStoredUser implementations
- **Severity:** P2
- **Affected Files:** `frontend/src/services/authService.js:6-14`, `frontend/src/services/authStorage.js:3-14`
- **Impact:** Two copies diverge.
- **Recommended Fix:** Single source of truth — import from authStorage.
- **Fix Complexity:** Low
- **Groupable:** Yes (frontend dedup group)

### P2-30 — frontend unused service methods
- **Severity:** P2
- **Affected Files:** `frontend/src/services/chatService.js:31-40`
- **Impact:** Dead code increases bundle size.
- **Recommended Fix:** Remove unused methods.
- **Fix Complexity:** Low
- **Groupable:** Yes (frontend dead code group)

### P2-31 — frontend no error boundary — white screen on crashes
- **Severity:** P2
- **Affected Files:** `frontend/src/App.jsx`
- **Impact:** Any component crash destroys entire UI.
- **Recommended Fix:** Add React Error Boundary.
- **Fix Complexity:** Low
- **Groupable:** Independent

---

## P3 — LOW / MAINTAINABILITY / COSMETIC

### P3-01 — Deprecated datetime.utcnow() in chat_history.py
- **Severity:** P3
- **Affected Files:** `backend/services/chat_history.py:46`
- **Impact:** Deprecated in Python 3.12+.
- **Recommended Fix:** Use `datetime.now(timezone.utc)`.
- **Fix Complexity:** Low
- **Groupable:** Yes (chat_history group)

### P3-02 — RegisterRequest.name allows Unicode control characters
- **Severity:** P3
- **Affected Files:** `backend/models/request_models.py:38-39`
- **Impact:** BIDI override, homoglyph attacks possible.
- **Recommended Fix:** Strip control characters or restrict to printable.
- **Fix Complexity:** Low
- **Groupable:** Yes (model validation group)

### P3-03 — UserStore._normalize_users silently handles missing hashed_password
- **Severity:** P3
- **Affected Files:** `backend/auth/user_store.py:34-45`
- **Impact:** Empty password hash creates confusing login failures.
- **Recommended Fix:** Log warning for missing hash.
- **Fix Complexity:** Low
- **Groupable:** Yes (user_store group)

### P3-04 — streaming_service media_type text/plain may contain markdown
- **Severity:** P3
- **Affected Files:** `backend/services/streaming_service.py:18-20`
- **Impact:** Text stream contains markdown/emoji. Using text/plain loses formatting.
- **Recommended Fix:** Document expectations. Consider text/event-stream.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P3-05 — utils/__init__.py missing
- **Severity:** P3
- **Affected Files:** `utils/` (directory)
- **Impact:** Namespace package behavior. Can cause import issues.
- **Recommended Fix:** Add empty `__init__.py`.
- **Fix Complexity:** Trivial
- **Groupable:** Independent

### P3-06 — schemas __init__.py empty — no exports
- **Severity:** P3
- **Affected Files:** `schemas/__init__.py`
- **Impact:** Forces importers to know exact module paths.
- **Recommended Fix:** Add `__all__` and re-exports.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P3-07 — backend/services/__init__.py has unused imports
- **Severity:** P3
- **Affected Files:** `backend/services/__init__.py`
- **Impact:** `json`, `os` imported but unused.
- **Recommended Fix:** Remove unused imports.
- **Fix Complexity:** Trivial
- **Groupable:** Independent

### P3-08 — config/*.py hardcoded values not env-driven
- **Severity:** P3
- **Affected Files:** `config/llm_config.py:6`, `config/college_config.py:8-10`
- **Impact:** localhost URL, thresholds cannot be tuned without code change.
- **Recommended Fix:** Add env var overrides.
- **Fix Complexity:** Low
- **Groupable:** Yes (config group)

### P3-09 — .gitignore has duplicate trailing entries
- **Severity:** P3
- **Affected Files:** `.gitignore:24-31`
- **Impact:** Corrupted file from append operations.
- **Recommended Fix:** Remove duplicates.
- **Fix Complexity:** Trivial
- **Groupable:** Independent

### P3-10 — test_streaming_service substring assertions are brittle
- **Severity:** P3
- **Affected Files:** `tests/test_streaming_service.py:8-13`
- **Impact:** Can pass with incorrect chunks.
- **Recommended Fix:** Assert exact chunks or total length.
- **Fix Complexity:** Low
- **Groupable:** Independent

### P3-11 — tests lacking edge case coverage
- **Severity:** P3
- **Affected Files:** `tests/test_pdf_routes.py`, `tests/test_pdf_service.py`
- **Impact:** Only 3-5 tests per file. Missing symlink, null byte, size limit tests.
- **Recommended Fix:** Add comprehensive security edge case tests.
- **Fix Complexity:** Low
- **Groupable:** Yes (test coverage group)

### P3-12 — frontend inline styles instead of CSS classes
- **Severity:** P3
- **Affected Files:** `frontend/src/components/MarkdownRenderer.jsx`, `ChatWindow.jsx`, `LandingPage.jsx`, `Login.jsx`, `Register.jsx`
- **Impact:** Prevents theming, increases bundle size.
- **Recommended Fix:** Extract to CSS classes.
- **Fix Complexity:** High
- **Groupable:** Independent

### P3-13 — frontend no memoization on expensive components
- **Severity:** P3
- **Affected Files:** `frontend/src/components/MarkdownRenderer.jsx`, `ChatWindow.jsx`, `MessageBubble.jsx`, `ChatPage.jsx`
- **Impact:** Re-renders entire message list on every update.
- **Recommended Fix:** Add React.memo, useMemo, useCallback.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend perf group)

### P3-14 — frontend magic strings throughout
- **Severity:** P3
- **Affected Files:** `frontend/src/store/chatStore.js`, `components/MessageBubble.jsx`, `ChatInput.jsx`
- **Impact:** Hard to internationalize, prone to typos.
- **Recommended Fix:** Extract to constants file.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend maintainability group)

### P3-15 — frontend alert() usage for PDF validation
- **Severity:** P3
- **Affected Files:** `frontend/src/components/ChatInput.jsx:55`
- **Impact:** Blocking, unstyled browser alert.
- **Recommended Fix:** Use inline error state or toast.
- **Fix Complexity:** Low
- **Groupable:** Yes (frontend UX group)

### P3-16 — frontend no PropTypes or TypeScript
- **Severity:** P3
- **Affected Files:** `frontend/src/components/*.jsx`, `pages/*.jsx`
- **Impact:** No prop validation. Refactoring risky.
- **Recommended Fix:** Add PropTypes or migrate to TypeScript.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend type safety group)

### P3-17 — frontend missing ARIA labels
- **Severity:** P3
- **Affected Files:** `frontend/src/components/ChatInput.jsx`, `Sidebar.jsx`
- **Impact:** Screen readers can't describe icon-only buttons.
- **Recommended Fix:** Add aria-label attributes.
- **Fix Complexity:** Low
- **Groupable:** Yes (frontend a11y group)

### P3-18 — frontend no keyboard navigation
- **Severity:** P3
- **Affected Files:** `frontend/src/components/ChatWindow.jsx`, `Sidebar.jsx`
- **Impact:** Violates WCAG.
- **Recommended Fix:** Add tabIndex and keyboard handlers.
- **Fix Complexity:** Medium
- **Groupable:** Yes (frontend a11y group)

### P3-19 — frontend no debounce on search filter
- **Severity:** P3
- **Affected Files:** `frontend/src/pages/ChatPage.jsx:34-38`
- **Impact:** Filters on every keystroke.
- **Recommended Fix:** Use useDebouncedCallback.
- **Fix Complexity:** Low
- **Groupable:** Yes (frontend perf group)

### P3-20 — frontend unused imports
- **Severity:** P3
- **Affected Files:** `frontend/src/pages/Register.jsx:9` (useAuth unused)
- **Impact:** Minor inconsistency.
- **Recommended Fix:** Remove unused import.
- **Fix Complexity:** Trivial
- **Groupable:** Yes (frontend cleanup group)

---

## STATISTICS

| Severity | Count |
|----------|-------|
| P0       | 11    |
| P1       | 13    |
| P2       | 31    |
| P3       | 20    |
| **Total**| **75**|

## TOP GROUPED FIX PACKAGES

| Group | Issues | Theme | Est. Complexity |
|-------|--------|-------|-----------------|
| G1    | P0-01,02 + P1-02,03 + P2-09 + P3-02,03 | jwt_service + user_store + model validation | Low-Medium |
| G2    | P0-04,05 + P1-12 + P2-04 + P3-08 | Auth security hardening | Medium |
| G3    | P0-06,07,08 + P2-10,25 + P3-01 | ChatHistory + UserStore safety | Medium |
| G4    | P0-03 + P2-01,02,03 + P2-21,23 | PDF upload, streaming, memory | Medium |
| G5    | P0-10 + P1-09,10 + P2-26,27,28,29,30 | Frontend security & async | Medium |
| G6    | P2-11,13,14,15,16,17 + P2-18,19,20 | Pipeline efficiency & tools | Low-Medium |
| G7    | P2-05,22 + P3-07 | Route refactoring & cleanup | Low |
| G8    | P3-12,13,14,15,16,17,18,19,20 | Frontend maintainability | Medium-High |

---

*END OF AUDIT_REPORT_V3.md*
