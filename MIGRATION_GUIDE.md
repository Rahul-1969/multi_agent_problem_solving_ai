# Migration Guide for Custom Code

If your code directly imports agents (instead of using `run_agents()`), here's how to migrate.

## Scenario 1: Using `base_agent()` directly

### Before

```python
from agents.base_agent import base_agent

answer = base_agent("What is recursion?")
print(answer)  # "Recursion is when a function calls itself..."
```

### After

```python
from agents.base_agent import base_agent

result = base_agent("What is recursion?")
print(result.answer)  # "Recursion is when a function calls itself..."

# You can also access metadata now
print(f"Confidence: {result.confidence}")
print(f"Tokens: {result.tokens}")
```

**Change**: `base_agent()` returns `AgentResult` instead of `str`.  
**Migration**: Extract `.answer` attribute instead of using result as string.

---

## Scenario 2: Using `refine_answer()` directly

### Before

```python
from agents.refiner_agent import refine_answer

answer = "Python is a programming language used for AI"
refined = refine_answer(answer)
print(refined)  # "Python is used for AI"
```

### After

```python
from agents.refiner_agent import refine_answer
from agents.models import AgentResult

# Create AgentResult from string (only needed if you don't have one)
result = AgentResult(answer="Python is a programming language used for AI")

# Pass AgentResult
refined = refine_answer(result)
print(refined.answer)  # "Python is used for AI"
```

**Change**: `refine_answer()` now accepts and returns `AgentResult`.  
**Migration**: Wrap string in `AgentResult` if needed, extract `.answer`.

---

## Scenario 3: Using `expert_enhance()` directly

### Before

```python
from agents.expert_agent import expert_enhance

answer = "Quicksort sorts in O(n log n) average case"
insight = expert_enhance(answer)
print(insight)  # "Worst case is O(n²) when pivot is poorly chosen"
```

### After

```python
from agents.expert_agent import expert_enhance
from agents.models import AgentResult

query = "What is quicksort?"
result = AgentResult(answer="Quicksort sorts in O(n log n) average case")

# expert_enhance() now needs the original query for context
enhanced = expert_enhance(result, query)
print(enhanced.answer)
# "Quicksort sorts in O(n log n) average case\n\n**Expert Insight:**\n..."
```

**Change**: `expert_enhance()` now accepts `AgentResult` + `query`, returns `AgentResult`.  
**Migration**: Create `AgentResult`, pass query, extract `.answer`.

---

## Scenario 4: Custom pipeline using multiple agents

### Before

```python
from agents.base_agent import base_agent
from agents.refiner_agent import refine_answer
from agents.expert_agent import expert_enhance

query = "Explain dynamic programming"

answer = base_agent(query)
answer = refine_answer(answer)
answer = expert_enhance(answer)

print(answer)
```

### After Option A: Use `run_agents()` (Recommended)

```python
from utils.agent_executor import run_agents

query = "Explain dynamic programming"
answer = run_agents(query, complexity_override="high")
print(answer)
```

✅ Simpler, uses adaptive policies, integrates statistics.

### After Option B: Use agents with new signatures (If you need fine control)

```python
from agents.base_agent import base_agent
from agents.refiner_agent import refine_answer
from agents.expert_agent import expert_enhance
from agents.agent_policy import should_run_refiner, should_run_expert

query = "Explain dynamic programming"
complexity = "high"

# Base agent
result = base_agent(query)

# Refiner (conditional)
if should_run_refiner(result, complexity):
    result = refine_answer(result)

# Expert (conditional)
if should_run_expert(result, complexity):
    result = expert_enhance(result, query)

print(result.answer)
```

✅ Full control with adaptive policies.

---

## Scenario 5: Getting metadata

### New Capability: Access execution metadata

```python
from agents.base_agent import base_agent
from agents.agent_policy import should_run_refiner, should_run_expert

result = base_agent("What is a hash table?")

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")  # 0.95
print(f"Tokens: {result.tokens}")  # 45
print(f"Can refine: {result.should_refine}")  # True
print(f"Needs expert: {result.should_expert}")  # False
```

---

## Scenario 6: Error handling

### Before

```python
from agents.base_agent import base_agent

try:
    answer = base_agent(query)
except Exception as e:
    answer = "Error processing query"
```

### After (Same behavior)

```python
from agents.base_agent import base_agent

try:
    result = base_agent(query)
    answer = result.answer
except Exception as e:
    answer = "Error processing query"
```

✅ Exception handling unchanged.  
⚠️ Note: Refiner and expert now degrade gracefully instead of raising.

```python
from agents.refiner_agent import refine_answer
from agents.models import AgentResult

result = AgentResult(answer=answer)
# If refine fails, it returns the input unchanged (no exception)
refined = refine_answer(result)  # Safe - won't raise
```

---

## Scenario 7: Testing with mock agents

### Before

```python
from unittest.mock import patch

with patch('agents.base_agent.call_llm') as mock_llm:
    mock_llm.return_value = "Test answer"
    result = base_agent("test query")
    assert result == "Test answer"
```

### After

```python
from unittest.mock import patch

with patch('agents.base_agent.call_llm') as mock_llm:
    mock_llm.return_value = "Test answer"
    result = base_agent("test query")
    assert result.answer == "Test answer"
    assert result.confidence > 0
    assert result.tokens > 0
```

---

## Scenario 8: Logging and observability

### New: Automatic logging from executor

```python
# Just use run_agents() - it logs everything
from utils.agent_executor import run_agents

answer = run_agents("What is recursion?")
# Logs: Agents | complexity=low | tokens=60 | confidence=0.95 | refiner=no | expert=no | elapsed=15.23s
```

### Custom logging with agents

```python
from agents.base_agent import base_agent
import logging

logger = logging.getLogger(__name__)

result = base_agent("What is recursion?")
logger.info(
    "Base agent: tokens=%d, confidence=%.2f",
    result.tokens,
    result.confidence,
)
```

---

## Scenario 9: Caching results

### Before

```python
cache = {}

def cached_answer(query):
    if query in cache:
        return cache[query]

    from agents.base_agent import base_agent
    answer = base_agent(query)
    cache[query] = answer
    return answer
```

### After

```python
cache = {}

def cached_answer(query):
    if query in cache:
        return cache[query]

    from utils.agent_executor import run_agents
    answer = run_agents(query)
    cache[query] = answer
    return answer
```

✅ Same pattern, but uses smart adaptive execution.

---

## Scenario 10: Streaming or partial results

### Before

Not possible - agents always return complete answers.

### After

Can access intermediate results:

```python
from agents.base_agent import base_agent
from agents.refiner_agent import refine_answer

# Get base answer immediately
base_result = base_agent(query)
print("Initial thought:", base_result.answer)
print("Confidence:", base_result.confidence)

# Then optionally refine
if base_result.confidence < 0.8:
    refined = refine_answer(base_result)
    print("Refined answer:", refined.answer)
```

✅ New capability with AgentResult.

---

## Migration Checklist

- [ ] Replace string returns with `.answer` extraction
- [ ] Update agents that call other agents to handle `AgentResult`
- [ ] Add query parameter to `expert_enhance()` calls
- [ ] Consider using `run_agents()` for simplified code
- [ ] Update error handling (refiner/expert now degrade gracefully)
- [ ] Add logging for observability
- [ ] Test with new metadata attributes
- [ ] Update type hints if using type checking

---

## Backward Compatibility Status

| Component          | Status       | Notes                                    |
| ------------------ | ------------ | ---------------------------------------- |
| `run_agents()`     | ✅ Unchanged | Same signature, same return type         |
| All pipelines      | ✅ Unchanged | Still call `run_agents(query)`           |
| Backend APIs       | ✅ Unchanged | Still receive string responses           |
| `base_agent()`     | ⚠️ Changed   | Returns `AgentResult`, was `str`         |
| `refine_answer()`  | ⚠️ Changed   | Accepts/returns `AgentResult`, was `str` |
| `expert_enhance()` | ⚠️ Changed   | Needs query parameter, was optional      |

**If using `run_agents()`: No migration needed.**  
**If using agents directly: Minor updates needed (see above).**

---

## Recommended Action

1. **Most code**: No change needed (uses `run_agents()`)
2. **If direct agent use**:
   - Extract `.answer` from results
   - Create `AgentResult` if needed
   - Add query to `expert_enhance()` calls
3. **New code**: Use `run_agents()` for simplicity

All changes are straightforward and low-risk.
