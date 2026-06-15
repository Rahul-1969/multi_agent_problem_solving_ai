## Pipeline Refactoring Architecture & Usage Guide

### Quick Reference

#### Old Way (String-based)

```python
def my_pipeline(query: str) -> str:
    response = "formatted output..."
    return response  # Formatter must parse this
```

#### New Way (Structured)

```python
from pipelines.pipeline_result import PipelineResult
from backend.models.response_models import EducationData

def my_pipeline(query: str) -> PipelineResult:
    response = "formatted output..."
    data = EducationData(topic=query, definition="...", ...)
    return PipelineResult(response=response, data=data)
```

---

## Using Schema Labels

### Before (Scattered)

```python
# In response_formatter.py
_EDUCATION_LABELS = {
    "definition": ["📖  Definition"],
    ...
}

# In education_pipeline.py
_SECTION_LABELS = {
    "definition": ["DEFINITION"],  # DIFFERENT!
    ...
}
```

### After (Centralized)

```python
# Use shared schema
from schemas.education_schema import EDUCATION_LABELS
from utils.section_parser import parse_sections

sections = parse_sections(text, EDUCATION_LABELS)
```

---

## Complete Pipeline Migration Example

### Step 1: Import Required Modules

```python
from pipelines.pipeline_result import PipelineResult
from schemas.my_schema import MY_LABELS
from backend.models.response_models import MyData
from utils.section_parser import parse_sections
```

### Step 2: Update Signature

```python
# OLD
def my_pipeline(query: str) -> str:

# NEW
def my_pipeline(query: str) -> PipelineResult:
```

### Step 3: Generate Formatted Response (unchanged)

```python
# Same logic as before
formatted_response = f"Header\n{_DIVIDER}\n\nContent..."
```

### Step 4: Parse into Model

```python
sections = parse_sections(formatted_response, MY_LABELS)

my_data = MyData(
    field1=sections.get("label1", "").strip() or None,
    field2=sections.get("label2", "").strip() or None,
    # ... other fields
)
```

### Step 5: Return PipelineResult

```python
return PipelineResult(response=formatted_response, data=my_data)
```

---

## Error Handling

### With Empty Data

```python
try:
    result = perform_operation()
except Exception as exc:
    logger.error("Pipeline error: %s", exc)
    return PipelineResult(
        response="⚠️ Error message",
        data=MyData()  # Empty model
    )
```

---

## Backward Compatibility in chatbot_service

```python
# chatbot_service AUTOMATICALLY handles both:

# NEW: PipelineResult with data
pipeline_result = education_pipeline(query)
if isinstance(pipeline_result, PipelineResult):
    response = pipeline_result.response  # Use response
    data = pipeline_result.data.model_dump()  # Use structured data
    logger.info("Pipeline returned structured data | type=EducationData")

# LEGACY: Plain string (if old pipeline still used)
string_result = general_pipeline(query)
if isinstance(string_result, str):
    response = string_result
    data = format_general(response)  # Parse with formatter
    logger.debug("Pipeline returned string (legacy)")
```

**No changes needed to routes or frontend.**

---

## Type System

### Type Aliases

```python
from typing import Final, TypeAlias, Mapping

LabelMap: TypeAlias = Mapping[str, list[str]]
Pattern: TypeAlias = re.Pattern[str]
PipelineData: TypeAlias = EducationData | MedicalData | CodingData | CollegeData | GeneralData | None
```

### Using in Functions

```python
def parse_by_schema(text: str, labels: LabelMap) -> dict[str, str]:
    # Type-safe, clear intent
    ...

@dataclass(slots=True)
class PipelineResult:
    response: str
    data: PipelineData = None

    def __post_init__(self) -> None:
        if not self.response or not isinstance(self.response, str):
            raise ValueError("response must be non-empty string")
```

---

## Schema File Template

Create `schemas/domain_schema.py`:

```python
"""
schemas/domain_schema.py
Canonical label definitions for [domain] domain.

Canonical section names:
  - field1: Description
  - field2: Description

Used by:
  - domain_pipeline
  - response_formatter
  - schema_parser
"""

from typing import Final, TypeAlias, Mapping


LabelMap: TypeAlias = Mapping[str, list[str]]


DOMAIN_LABELS: Final[LabelMap] = {
    "field1": ["Primary Label", "Alias 1", "Alias 2"],
    "field2": ["Another Label"],
}

__all__ = ["DOMAIN_LABELS", "LabelMap"]
```

---

## Integration Checklist

When adding a new pipeline:

- [ ] Create `schemas/domain_schema.py` with labels
- [ ] Create `pipelines/domain_pipeline.py` returning PipelineResult
- [ ] Create corresponding `DomainData` model in response_models.py
- [ ] Add pipeline to `_PIPELINES` in chatbot_service.py
- [ ] Add routing logic to router.domain_router
- [ ] Import schema labels in pipeline
- [ ] Parse response into model using labels
- [ ] Return PipelineResult(response=str, data=model)
- [ ] Test backward compatibility (chatbot_service handles both)
- [ ] Verify logs show "Pipeline returned structured data"

---

## FAQ

### Q: What if my pipeline generates sections the formatter doesn't recognize?

**A:** Add them to the schema labels. Example:

```python
EDUCATION_LABELS = {
    "definition": ["📖  Definition"],
    "new_section": ["NEW SECTION"],  # Add here
}
```

### Q: Can I run both old and new pipelines simultaneously?

**A:** Yes! chatbot_service uses isinstance() to detect both PipelineResult and str.
Migrate one pipeline at a time.

### Q: What happens if PipelineResult.data is None?

**A:** chatbot_service falls back to formatter:

```python
if result.data:
    return result.data.model_dump()  # Use data
else:
    return format_domain(result.response)  # Fallback
```

### Q: Do I need to update the routes?

**A:** No. Routes still receive ChatResponse with same structure.
Data field is now always populated (instead of sometimes missing).

### Q: How do I debug data parsing?

**A:** Look for logs:

- "Pipeline returned structured data | type=..." = Success
- "PipelineResult had no data, using formatter" = Fallback
- "Pipeline returned string (legacy)" = Old format

### Q: Can I remove response_formatter.py?

**A:** Yes, but wait until ALL pipelines return PipelineResult.
Then chatbot_service won't need formatters anymore.

---

## Architecture Diagram

```
Current Flow (After Refactoring)
════════════════════════════════

User Query
    ↓
router.domain_router (detect domain)
    ↓
_PIPELINES[domain] (get pipeline function)
    ↓
Pipeline Function
    ├─ Call LLM
    ├─ Generate formatted string
    ├─ Parse using schema labels
    ├─ Build domain model
    └─ Return PipelineResult(response, data)
    ↓
chatbot_service._extract_structured_data()
    ├─ Check isinstance(PipelineResult)
    ├─ If yes: extract data → model_dump()
    └─ If no: use formatter → model_dump()
    ↓
ChatResponse(success, domain, response, data)
    ↓
API Route → Frontend
```

---

## Performance Characteristics

| Aspect        | Impact   | Notes                             |
| ------------- | -------- | --------------------------------- |
| LLM calls     | None     | Same as before                    |
| Parsing speed | Same     | Reuses section_parser             |
| Memory usage  | +5-10KB  | PipelineResult slots optimization |
| Type checking | Improved | Full type hints enable IDE help   |
| Debugging     | Better   | Structured data vs strings        |
| Deployment    | Gradual  | Mix old and new during transition |

---

## Migration Timeline

### Phase 1: Setup (✅ Complete)

- Create PipelineResult
- Create schema files
- Update chatbot_service

### Phase 2: Pipeline Migration (Your Next Steps)

- Migrate education_pipeline ✅
- Migrate medical_pipeline ✅
- Migrate coding_pipeline ✅
- Migrate general_pipeline ✅
- Migrate college_pipeline ✅

### Phase 3: Cleanup (Future)

- All pipelines return PipelineResult
- Remove formatter dispatch logic
- Delete response_formatter.py

---

## Code Examples

### Example 1: Minimal Pipeline

```python
from pipelines.pipeline_result import PipelineResult
from backend.models.response_models import GeneralData

def general_pipeline(query: str) -> PipelineResult:
    response = f"Answer to '{query}': ..."
    return PipelineResult(response=response, data=GeneralData(answer=response))
```

### Example 2: Complex Pipeline with Sections

```python
from pipelines.pipeline_result import PipelineResult
from schemas.education_schema import EDUCATION_LABELS
from utils.section_parser import parse_sections
from backend.models.response_models import EducationData

def education_pipeline(query: str) -> PipelineResult:
    # Generate formatted output (existing logic)
    response = f"📚 Topic\n{divider}\n\n📖  Definition\nDef text\n\n🔑  Key Points\n- Point 1"

    # Parse into structured model
    sections = parse_sections(response, EDUCATION_LABELS)
    data = EducationData(
        topic=query,
        definition=sections.get("definition", "").strip() or None,
        key_points=sections.get("key_points", "").strip() or None,
        example=sections.get("example", "").strip() or None,
        exam_tip=sections.get("exam_tip", "").strip() or None,
    )

    return PipelineResult(response=response, data=data)
```

### Example 3: Error Handling

```python
def my_pipeline(query: str) -> PipelineResult:
    try:
        # Pipeline logic
        result = perform_pipeline(query)
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc)
        return PipelineResult(
            response=f"⚠️ Error: {exc}",
            data=MyData()  # Return empty model
        )

    # Parse result into model...
    return PipelineResult(response=formatted, data=model)
```

---

## Summary

✅ Centralized schema definitions (single source of truth)
✅ Structured data flow (PipelineResult)
✅ Backward compatible (handles both new and old formats)
✅ Type safe (Final, TypeAlias, dataclasses)
✅ Gradual migration (migrate one pipeline at a time)
✅ Future-proof (easy to add new agents/domains)

All pipelines are ready to return PipelineResult. Enjoy!
