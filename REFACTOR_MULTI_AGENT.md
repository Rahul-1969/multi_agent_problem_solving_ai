# Multi-Agent Refactoring Documentation

## Overview

The multi-agent system has been refactored to support **adaptive execution** and reduce unnecessary LLM calls. The new architecture uses a **policy layer** to make smart decisions about which agents should run based on query complexity, answer confidence, and other metadata.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│           Query Processing Flow                         │
└─────────────────────────────────────────────────────────┘

    User Query
        ↓
    detect_complexity(query)
        ↓
    ┌───────────────────────┐
    │  Base Agent           │  (always runs)
    │  - Direct answer      │  1 LLM call
    │  - Confidence: 0.0-1.0│  ~250 tokens
    │  - Returns: AgentResult│
    └───────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │ should_run_refiner()            │
    │ - low → skip                    │
    │ - medium/high → run             │
    └─────────────────────────────────┘
        ↙           ↘
      YES           NO
       ↓             ↓
   ┌──────────┐   [skip]
   │  Refiner │     ↓
   │ - Compress│  ←─┘
   │ - Clarify │
   └──────────┘
       ↓
    ┌─────────────────────────────────┐
    │ should_run_expert()             │
    │ - Check confidence              │
    │ - Check length                  │
    │ - Check tokens                  │
    └─────────────────────────────────┘
        ↙           ↘
      YES           NO
       ↓             ↓
   ┌──────────┐   [skip]
   │  Expert  │     ↓
   │ - 1 insight    ←─┘
   │ - 1 caveat     │
   │ - 1 optimization
   └──────────┘
       ↓
    Final Answer
        ↓
    Log Statistics
        ↓
    Return String
```

## File Changes

### New Files

#### `agents/models.py`

Defines the `AgentResult` dataclass with slots for memory efficiency:

```python
@dataclass(slots=True)
class AgentResult:
    answer: str              # The generated response
    confidence: float = 1.0  # 0.0-1.0, model certainty
    tokens: int = 0          # Estimated token count
    should_refine: bool = True    # Refiner can run
    should_expert: bool = False   # Expert can run
```

**Purpose**: Flows metadata (confidence, tokens) between agents instead of just passing raw strings.

#### `agents/agent_policy.py`

Implements decision logic for adaptive execution:

```python
def should_run_refiner(result: AgentResult, complexity: str) -> bool:
    """
    Rules:
    - low: skip (base is good enough)
    - medium/high: always run
    """

def should_run_expert(result: AgentResult, complexity: str) -> bool:
    """
    Rules:
    - Skip if not high complexity
    - For high: check confidence, length, tokens
    """
```

**Purpose**: Centralizes policy decisions. Easy to extend for new agents without modifying executor.

### Modified Files

#### `agents/base_agent.py`

- **Returns**: `AgentResult` (not `str`)
- **New**: Token estimation and confidence calculation
- **Heuristics**:
  - 100-300 chars → 0.95 confidence
  - <50 chars → 0.70 confidence (too brief)
  - > 500 chars → 0.75 confidence (rambling)

#### `agents/refiner_agent.py`

- **Accepts**: `AgentResult` (not `str`)
- **Returns**: `AgentResult`
- **Changes**:
  - Preserves confidence from base
  - Updates tokens based on refined answer
  - Graceful fallback on failure (returns input)

#### `agents/expert_agent.py`

- **Accepts**: `AgentResult` and `query` (not just answer)
- **Returns**: `AgentResult`
- **Changes**:
  - Adds one insight under "**Expert Insight:**" header
  - Preserves confidence
  - Graceful fallback on failure
  - Query context helps targeted insights

#### `utils/agent_executor.py`

Complete orchestration refactor:

**Old Flow**:

```python
answer = base_agent(query)
if level != "low":
    answer = refiner(answer)
if level == "high":
    answer = expert(query, answer)
return answer
```

**New Flow**:

```python
base_result = _run_base(query)

if should_run_refiner(base_result, level):
    base_result = _run_refiner(base_result)
else:
    # skip refiner

if should_run_expert(base_result, level):
    base_result = _run_expert(base_result, query)
else:
    # skip expert

return base_result.answer  # backward compatible
```

**New Features**:

- Execution statistics logging
- Graceful fallback on each failure
- Time tracking
- Policy-driven decisions

## Execution Patterns

### Low Complexity

```
Example: "what is a binary tree?"

base_agent(query)
  → confidence: 0.95
  → tokens: 60
  → answer: "A binary tree is a tree data structure..."

should_run_refiner? NO (low complexity)

Result: Base answer only (1 LLM call, ~60 tokens)
```

### Medium Complexity

```
Example: "explain the difference between quicksort and mergesort"

base_agent(query)
  → confidence: 0.85
  → tokens: 180

should_run_refiner? YES (medium complexity)

refiner_agent(result)
  → compresses answer
  → tokens: 140
  → confidence: 0.85 (preserved)

should_run_expert? NO (not high complexity)

Result: Base + Refined (2 LLM calls, ~140 tokens)
```

### High Complexity - Expert Included

```
Example: "write a function to find LCA in a BST"

base_agent(query)
  → confidence: 0.70 (uncertain)
  → tokens: 220

should_run_refiner? YES

refiner_agent(result)
  → tokens: 200
  → confidence: 0.70

should_run_expert? YES
  - confidence < 0.6? NO (0.70)
  - answer length > 50? YES
  - tokens < 400? YES
  → Policy: RUN (uncertainty + substance warrant expert)

expert_enhance(result, query)
  → adds: "Edge case: Handle null children..."
  → tokens: 280

Result: Base + Refined + Expert (3 LLM calls, ~280 tokens)
```

### High Complexity - Expert Skipped

```
Example: "write a sorting algorithm" (very short initial answer)

base_agent(query)
  → confidence: 0.95
  → tokens: 30
  → answer: "Sort an array." (too brief)

should_run_refiner? YES

refiner_agent(result)
  → tokens: 25 (still too short)
  → confidence: 0.95

should_run_expert? NO
  - answer length (25) < MIN (50): SKIP
  - "Answer too short" reason logged

Result: Base + Refined, Expert Skipped (2 LLM calls, ~25 tokens)
```

## Policy Decision Thresholds

### Refiner Policy

| Complexity | Run Refiner | Reason                        |
| ---------- | ----------- | ----------------------------- |
| low        | ❌ NO       | Base answer is sufficient     |
| medium     | ✅ YES      | Always improve clarity        |
| high       | ✅ YES      | Prepare for expert refinement |

### Expert Policy

| Condition          | Skip Reason              |
| ------------------ | ------------------------ |
| complexity != high | Not high complexity      |
| len(answer) < 50   | Answer too short         |
| confidence >= 0.6  | Confidence too high      |
| tokens >= 400      | Tokens approaching limit |
| ✅ All pass        | Run expert               |

## Logging & Execution Statistics

Every execution logs:

```
Agents | complexity=medium | tokens=140 | confidence=0.85 | \
        refiner=yes | expert=no | elapsed=85.23s
```

Useful for:

- Monitoring LLM call counts
- Tracking average response quality
- Analyzing pipeline latency
- Debugging policy decisions

## Backward Compatibility

✅ **Fully maintained**:

- `run_agents(query) -> str` interface unchanged
- All pipelines continue to call `run_agents()`
- AgentResult abstraction is **internal only**
- Return value is always a plain string

## Error Handling

Graceful degradation at each stage:

| Stage   | Failure Handling                     |
| ------- | ------------------------------------ |
| Base    | Return error message (can't proceed) |
| Refiner | Return base result as-is             |
| Expert  | Return refiner result as-is          |

Never crashes the pipeline.

## Extensibility

Adding a new agent (e.g., `fact_checker_agent`) requires:

1. Create the agent: `agents/fact_checker_agent.py`

   ```python
   def fact_check(result: AgentResult) -> AgentResult:
       """Check facts in answer"""
   ```

2. Add policy: Add function to `agents/agent_policy.py`

   ```python
   def should_run_fact_checker(result, complexity):
       """Decide when to fact-check"""
   ```

3. Update executor: Add orchestration in `utils/agent_executor.py`
   ```python
   if should_run_fact_checker(result, level):
       result = _run_fact_checker(result)
   ```

No complex refactoring needed.

## Performance Impact

| Level  | Old Calls | New Calls | Change | Benefit                           |
| ------ | --------- | --------- | ------ | --------------------------------- |
| low    | 1         | 1         | —      | No change                         |
| medium | 2         | 2         | —      | No change                         |
| high   | 3         | 2-3       | ↓ ~30% | Skip expert for confident answers |

For high-complexity queries where base is confident (0.95+), expert is skipped entirely, saving ~40-50 seconds per call.

## Future Enhancements

Ready to add without executor changes:

- `memory_agent` - Remember context from previous queries
- `retrieval_agent` - Look up external sources
- `citation_agent` - Track sources
- `critic_agent` - Evaluate answer quality
- `fact_checker_agent` - Verify claims
- `streaming_agent` - Token-by-token responses
- `parallel_agents` - Run agents concurrently

Each just needs its own policy and agent function.

## Files Summary

| File                      | Purpose               | Type     |
| ------------------------- | --------------------- | -------- |
| `agents/models.py`        | AgentResult dataclass | NEW      |
| `agents/agent_policy.py`  | Decision logic        | NEW      |
| `agents/base_agent.py`    | Initial answer        | MODIFIED |
| `agents/refiner_agent.py` | Compress & clarify    | MODIFIED |
| `agents/expert_agent.py`  | Add insight           | MODIFIED |
| `utils/agent_executor.py` | Orchestration         | MODIFIED |
