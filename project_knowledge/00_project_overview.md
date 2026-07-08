# Project Overview

- **Purpose**
  - Generate a weekly Telegram monitoring report for the official Telegram channels of Namangan region local councils.
  - Turn channel posts into a structured weekly compliance/reporting package based on a fixed classification taxonomy and a fixed report template.
  - Preserve reference-driven business logic: authoritative classification rules, authoritative narrative rules, and a reference DOCX layout.

- **Expected output**
  - One report run produces one reporting package for one weekly period.
  - Final human-facing output is a DOCX weekly report in Uzbek, generated from the reference report template.
  - Intermediate machine artifacts are written under `data/` as JSON at each pipeline stage:
    - raw posts
    - classified posts
    - classification regression report
    - audited posts
    - audit regression report
    - aggregated statistics
    - narrative
    - narrative validation report

- **High-level pipeline**
  - Determine report period in `Asia/Tashkent`.
  - Fetch Telegram posts from the configured monitored channels.
  - Exclude posts without substantive text, including media without caption/text.
  - Classify posts into the approved category system using Gemini and the authoritative classification specification.
  - Validate every classification result with deterministic regression checks.
  - Re-audit every classified post with Gemini against the same authoritative specification.
  - Validate audited results with deterministic regression checks.
  - Aggregate audited posts into per-channel and overall weekly statistics.
  - Generate Uzbek narrative sections only from deterministic aggregated facts.
  - Validate narrative language and numbers deterministically.
  - Produce the final DOCX by updating the reference report document in place.

- **Major subsystems**
  - **Configuration and run context**
    - YAML config, environment-based secrets, report-period calculation, timezone handling, run directory setup.
  - **Telegram ingestion**
    - Telegram authentication/session handling, channel traversal, weekly post extraction, subscriber/view capture.
  - **Classification subsystem**
    - Authoritative taxonomy loading, reference dataset loading, Gemini batch classification, structured result normalization.
  - **Validation subsystem**
    - Deterministic checks for category validity, rule consistency, required evidence, required dataset references, and field-level invariants.
  - **Audit subsystem**
    - Full-post re-audit of classification outputs using the same taxonomy and the same structured output contract.
  - **Aggregation subsystem**
    - Per-channel and system-wide category totals, breakdowns, daily counts, view metrics, and aggregation identity checks.
  - **Narrative subsystem**
    - Fact-only Uzbek narrative generation plus deterministic narrative validation.
  - **Report generation subsystem**
    - Reference-DOCX-based table and narrative population with final weekly file output.
