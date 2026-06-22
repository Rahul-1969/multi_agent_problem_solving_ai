# P0_TRIAGE_V3.md — P0 Finding Verification & Classification

**Date:** 2026-06-22
**Branch:** kimchi-p5-session
**Scope:** Verify all 11 P0 findings from AUDIT_REPORT_V3.md against actual source code.

---

## Classification Legend

| Class | Meaning |
|-------|---------|
| **REAL** | Confirmed present in source code. Requires fix. |
| **ALREADY FIXED** | Already addressed in current codebase (prior session or by design). |
| **LOW PRIORITY** | Technically present but impact is minimal / theoretical only. |
| **REJECTED** | Finding is incorrect — code behavior does not match issue description. |
| **DOWNGRADE TO P1** | Present but severity overstated; belongs in P1. |
| **DOWNGRADE TO P2** | Present but minor; belongs in P2. |

---

## Triage Table

| V3 ID | Status | Classification | Rationale |
|-------|--------|----------------|-----------|
| P0-01 | ✅ Confirmed | **REAL** | `_ACCESS_SECRET_KEY` and `_REFRESH_SECRET_KEY` resolve to `None` when env vars missing. `SECRET_KEY` alias is also `None`. `_ensure_secrets()` defers error to first use, but any code that reads `SECRET_KEY` at import gets `None` silently. |
| P0-02 | ✅ Confirmed | **ALREADY FIXED** | `_ensure_secrets()` is called at the top of both `decode_token` and `_create_token`. If keys are `None`, `RuntimeError` is raised *before* `jwt.decode` or `jwt.encode` is invoked. PyJWT never receives `None`. Prior session's deferred-validation fix (P0-11) covers this. |
| P0-03 | ✅ Confirmed | **REAL** | `upload_pdf` uses `await file.read()` with no size check. No request body limit configured in `main.py`. DoS vector confirmed. |
| P0-04 | ✅ Confirmed | **REAL** | `_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false")...` defaults to `False`. Production behind HTTPS that forgets to set the env var will have cookies silently rejected by browsers. Auth appears broken with no visible error. |
| P0-05 | ✅ Confirmed | **REAL** | No rate limiting, account lockout, or CAPTCHA on `/auth/login`, `/auth/register`, `/auth/refresh`. Brute-force credential stuffing possible. |
| P0-06 | ✅ Confirmed | **REAL** | `user_store = UserStore()` (user_store.py:80) and `chat_history_manager = ChatHistoryManager()` (chat_history.py:124) execute at module import. `_load()` reads disk; `os.makedirs()` can fail with permission error and prevent app startup. Test isolation broken (state persists across tests). |
| P0-07 | ✅ Confirmed | **REAL** | `get_user`, `get_user_by_email`, `username_exists` read `self._users` without acquiring `self._lock`. Concurrent `create_user` (which holds the lock) can mutate dict during `get_user_by_email`'s `self._users.values()` iteration → `RuntimeError: dictionary changed size during iteration`. Additionally, `username_exists` does NOT normalize case (raw `username in self._users`) while `get_user` does (`str(username).strip().lower()`), allowing case-variation duplicate registrations. |
| P0-08 | ✅ Confirmed | **REAL** | `_persist` in ChatHistoryManager catches all `OSError` and passes silently. If disk is full / permissions revoked, chat data is accepted in memory but lost forever on restart. No ERROR log, no exception raised. |
| P0-09 | ⚠️ Partial | **DOWNGRADE TO P1** | Race condition technically exists (`global _df` check-then-act). However, FastAPI workers are separate processes, each with their own `_df`. Within a single process, pytest runs tests sequentially. Worst case is duplicate CSV load (wasteful, not corrupt). Impact is startup overhead, not runtime bug. |
| P0-10 | ✅ Confirmed | **REAL** | Major mismatch between frontend component destructuring and backend model fields. CodingResponse expects `time_complexity`, `space_complexity`, `key_points` — backend returns `complexity`, `tip`. AcademicResponse expects `key_formulas`, `tips`, `summary`, `diagram` — backend returns `key_points`, `exam_tip`. MedicalResponse expects `symptoms`, `possible_causes`, `recommendations` — backend returns `conditions`, `treatments`, `lifestyle`, `emergency`. **Structured response feature is completely non-functional.** |
| P0-11 | ✅ Confirmed | **REAL** | 12 of 14 JWT tests fail when `JWT_SECRET_KEY` / `JWT_ACCESS_SECRET_KEY` are not set in the environment at test time. Test module imports `jwt_service` at top level. `_ensure_secrets()` raises `RuntimeError` on first token creation. Tests are not self-contained. |

---

## Detailed Verifications

### P0-01 — JWT secret keys resolve to `None`
**Evidence:**
```python
# backend/auth/jwt_service.py:18-21
_ACCESS_SECRET_KEY: str | None = os.getenv("JWT_ACCESS_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
_REFRESH_SECRET_KEY: str | None = os.getenv("JWT_REFRESH_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
SECRET_KEY = _ACCESS_SECRET_KEY
```
If no env vars are set, all three are `None`. Any module that imports `SECRET_KEY` gets `None` silently. `_ensure_secrets()` defers the error, but import-time consumers are unprotected.

**Why REAL:** The `SECRET_KEY` export is a broken contract for import-time consumers.

---

### P0-02 — `decode_token` passes `None` key
**Evidence:**
```python
# backend/auth/jwt_service.py:72-84
def decode_token(token: str, expected_type: str | None = None) -> TokenPayload:
    _ensure_secrets()   # ← raises RuntimeError if keys are None
    key = _ACCESS_SECRET_KEY
    ...
    payload = jwt.decode(token, key, algorithms=[ALGORITHM])
```
The `_ensure_secrets()` call at line 73 unconditionally validates keys before PyJWT is invoked. If keys are `None`, `RuntimeError` is raised before line 81 executes.

**Why ALREADY FIXED:** Prior session (Phase 3, P0-11) introduced deferred validation. The V3 audit did not recognize that `_ensure_secrets()` prevents the `None` path.

---

### P0-03 — No file size limit on PDF upload
**Evidence:**
```python
# backend/api/routes/pdf.py:139-141
with open(save_path, "wb") as file_obj:
    content = await file.read()
    file_obj.write(content)
```
No `len(content)` check, no `file.size` check, no Starlette body-size limit middleware. `backend/main.py` configures no request size limits.

**Why REAL:** Unbounded memory allocation on upload. Direct DoS vector.

---

### P0-04 — Cookie `secure` defaults to `False`
**Evidence:**
```python
# backend/api/routes/auth.py:15
_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
```
Comment explicitly says "secure=False for localhost dev; set COOKIE_SECURE=true in production" — but if production omits the env var, the default is `False`. Modern browsers (Chrome 80+, Firefox) silently drop non-secure cookies over HTTPS.

**Why REAL:** Default must be secure for safety. Insecure should require explicit opt-in.

---

### P0-05 — No rate limiting on auth endpoints
**Evidence:** Zero decorators, middleware, or manual tracking in `backend/api/routes/auth.py`. No `slowapi`, no Redis counter, no account lockout logic in `user_store.py`.

**Why REAL:** Brute-force exposure is a direct security vulnerability.

---

### P0-06 — Singletons at import time
**Evidence:**
```python
# backend/auth/user_store.py:80
user_store = UserStore()
# backend/services/chat_history.py:124
chat_history_manager = ChatHistoryManager()
```
Both execute disk I/O at module import. `UserStore.__init__` calls `os.makedirs(DATA_DIR, exist_ok=True)` which can raise `PermissionError` at import time.

**Why REAL:** Breaks test isolation (tests mutate shared `users.json` and `chat_history.json`). Blocks startup if filesystem is unavailable.

---

### P0-07 — UserStore read paths have no lock
**Evidence:**
```python
# backend/auth/user_store.py:51-53
def get_user(self, username: str) -> dict[str, Any] | None:
    normalized = str(username).strip().lower()
    return self._users.get(normalized)   # ← no lock

# backend/auth/user_store.py:74-76
def username_exists(self, username: str) -> bool:
    return username in self._users   # ← no lock, no normalization
```
`get_user_by_email` iterates `self._users.values()` with generator — mutable during iteration.

**Why REAL:** Two distinct bugs: (1) race condition on dict iteration, (2) case-sensitivity mismatch allowing duplicate accounts.

---

### P0-08 — ChatHistoryManager._persist silently swallows OSError
**Evidence:**
```python
# backend/services/chat_history.py:36-42
def _persist(self) -> None:
    try:
        ...
        with open(_CHAT_HISTORY_FILE, "w", ...) as fh:
            json.dump(self._store, fh, ...)
    except OSError:
        pass   # ← silent swallow
```
No log, no re-raise. Disk-full = data loss with 200 OK to user.

**Why REAL:** Silent data loss is a critical reliability bug.

---

### P0-09 — data_loader.py thundering herd
**Evidence:**
```python
# tools/data_loader.py:48-56
_df: pd.DataFrame | None = None

def load_data() -> pd.DataFrame:
    global _df
    if _df is not None:
        return _df
    ...
    _df = df
    return _df
```
No `threading.Lock()`. Race exists but is bounded by process isolation.

**Why DOWNGRADE TO P1:** The race is real but the impact is duplicate loading (performance waste), not data corruption. FastAPI workers are processes, not threads, in typical uvicorn deployment.

---

### P0-10 — Frontend/backend data model mismatch
**Evidence (Frontend expectations):**
```javascript
// CodingResponse.jsx:11-18
const { code, language, explanation, output, time_complexity, space_complexity, key_points, title } = data;
// AcademicResponse.jsx:11-18
const { title, definition, explanation, example, diagram, key_formulas, tips, summary } = data;
// MedicalResponse.jsx:11-18
const { symptoms, possible_causes, recommendations, when_to_consult, disclaimer } = data;
```

**Evidence (Backend models):**
```python
# backend/models/response_models.py
class CodingData(BaseModel):
    language, code, explanation, complexity, tip, clarification

class EducationData(BaseModel):
    topic, definition, key_points, example, exam_tip

class MedicalData(BaseModel):
    conditions, treatments, lifestyle, emergency, disclaimer
```

Zero overlap on structured fields. Frontend always renders empty defaults.

**Why REAL:** Core feature (structured responses) is completely broken. Every domain response shows empty sections.

---

### P0-11 — 12 JWT tests fail without env var
**Evidence:**
```bash
$ pytest tests/test_jwt_service.py -x
FAILED test_jwt_service.py::TestTokenCreation::test_create_access_token_includes_type_claim
RuntimeError: JWT_ACCESS_SECRET_KEY or JWT_SECRET_KEY environment variable must be configured.
```
With `JWT_SECRET_KEY=test-secret`, all 14 tests pass. Without it, tests fail at first token creation.

**Why REAL:** Tests must be self-contained. CI environments may not have env vars pre-set.

---

## Grouped Fix Recommendations

### Group G1 — Auth Security & JWT (5 REAL issues)
**Issues:** P0-01, P0-04, P0-05, P0-11
**Theme:** Harden authentication layer
**Complexity:** Medium
**Dependencies:** P0-04 and P0-05 both in `backend/api/routes/auth.py`. P0-01 and P0-11 both in `backend/auth/jwt_service.py` and `tests/test_jwt_service.py`.

### Group G2 — User Store & Chat History Lifecycle (3 REAL issues)
**Issues:** P0-06, P0-07, P0-08
**Theme:** Singleton safety, threading, persistence reliability
**Complexity:** Medium
**Dependencies:** All three involve `backend/auth/user_store.py` or `backend/services/chat_history.py`. Can be fixed in a single backend-architecture pass.

### Group G3 — PDF Upload DoS (1 REAL issue)
**Issues:** P0-03
**Theme:** File upload security
**Complexity:** Medium
**Dependencies:** Standalone — only `backend/api/routes/pdf.py` and `backend/main.py`.

### Group G4 — Frontend/Backend Model Alignment (1 REAL issue)
**Issues:** P0-10
**Theme:** Data contract reconciliation
**Complexity:** High
**Dependencies:** Requires changes across pipelines (`pipelines/*`), schemas (`schemas/*`), response models (`backend/models/response_models.py`), and frontend components (`frontend/src/components/*`). Largest scoped fix. Should be its own batch.

---

## Summary

| Classification | Count | IDs |
|----------------|-------|-----|
| **REAL** | **8** | P0-01, P0-03, P0-04, P0-05, P0-06, P0-07, P0-08, P0-10, P0-11 |
| **ALREADY FIXED** | **1** | P0-02 |
| **DOWNGRADE TO P1** | **1** | P0-09 |
| DOWNGRADE TO P2 | 0 | — |
| LOW PRIORITY | 0 | — |
| REJECTED | 0 | — |

**Confirmed REAL P0 count: 8 issues requiring fixes.**
**Already fixed: 1 issue (P0-02, covered by prior deferred validation).**
**Downgraded: 1 issue (P0-09 → P1).**

---

*END OF P0_TRIAGE_V3.md*
