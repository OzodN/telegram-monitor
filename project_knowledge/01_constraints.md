# Hard Constraints

- **Execution model**
  - Single-machine execution.
  - Batch processing only.
  - Weekly execution model.
  - One run produces one report.
  - No always-on service requirement.

- **Architecture constraints**
  - No database.
  - No Docker dependency.
  - No microservices.
  - No REST API layer.
  - No message queue.
  - No CQRS/DDD/repository-pattern redesign assumptions.
  - File-based pipeline with JSON artifacts under `data/`.

- **Content and classification constraints**
  - Every post must receive exactly one category.
  - Category 1 is aggregate-only and not directly assignable.
  - Classification source of truth is `references/classification_specification_v2.md`.
  - Deprecated category instruction documents must not be used for classification decisions.
  - `24_ta_masala.md` and `Qonunlar_taqsimoti.md` are support/reference datasets, not taxonomy replacements.
  - Media without caption or substantive text must be ignored completely and must not enter downstream processing.

- **Narrative and report constraints**
  - Final report language is Uzbek.
  - Narrative source of truth is `references/narrative_specification_v1.md`.
  - Narrative must use only deterministic structured facts.
  - Narrative must not invent causes, motives, interpretations, unsupported trends, or unsupported numbers.
  - Final DOCX must follow the provided reference report template.

- **Operational constraints**
  - Telegram credentials come from environment variables or config indirection.
  - Gemini access supports multiple API keys in ordered rotation.
  - Low-touch weekly operation is assumed; output artifacts must be persisted to disk.
