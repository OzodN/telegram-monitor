# Current Architecture

- **Top-level flow**
  1. Load `.env` and `config.yaml`.
  2. Load classification specification and reference datasets.
  3. Initialize Gemini client with ordered API-key rotation and run-wide throttling.
  4. Create output directories under `data/`.
  5. Calculate the report period.
  6. Fetch weekly Telegram posts from configured channels.
  7. Persist raw posts.
  8. Classify posts in Gemini batches.
  9. Persist classified posts.
  10. Run deterministic classification regression checks.
  11. Audit all classified posts in Gemini batches.
  12. Persist audited posts.
  13. Run deterministic audit regression checks.
  14. Aggregate audited posts into per-channel and overall report statistics.
  15. Persist aggregated statistics.
  16. Generate Uzbek narrative from deterministic aggregation facts.
  17. Persist narrative.
  18. Validate narrative deterministically.
  19. Persist narrative validation report.
  20. Generate final DOCX from the reference report template.

- **Major components**
  - **Configuration layer**
    - `config_loader`
    - Resolves timezone, Telegram settings, Gemini settings, report-period settings, and reference/output paths.
  - **Reference-data layer**
    - `classification_support`
    - Loads:
      - authoritative classification specification
      - 24 issues dataset
      - 162 laws dataset
    - Builds canonical catalogs used by classification, audit, validation, and aggregation.
  - **Telegram ingestion layer**
    - `telegram_fetcher`
    - Responsibilities:
      - authorization/session handling
      - monitored-channel traversal
      - period-bounded post extraction
      - subscriber/view collection
      - exclusion of posts without usable text
  - **AI classification layer**
    - `classifier`
    - Input: raw Telegram posts
    - Output: structured classified posts with category, rule, evidence, and dataset references
  - **Deterministic validation layer**
    - `regression_checks`
    - Enforces field, rule, and dataset consistency after classification and after audit
  - **AI audit layer**
    - `auditor`
    - Input: classified posts
    - Output: fully re-audited classified posts with audit status
  - **Aggregation layer**
    - `aggregator`
    - Produces:
      - category totals
      - channel stats
      - daily counts
      - view metrics
      - category-specific breakdowns
      - aggregation identity checks
  - **Narrative layer**
    - `narrative_generator`
    - `narrative_validator`
    - Generates narrative only from aggregated facts and validates language/numeric compliance
  - **Report layer**
    - `report_generator`
    - Opens the reference DOCX, fills the header, table, and narrative paragraphs, and saves the weekly report

- **Primary data flow**
  - `Telegram posts -> classified posts -> audited posts -> aggregated report -> narrative -> validated DOCX report`

- **Persistent artifact layout**
  - `data/raw_posts/`
  - `data/classified_posts/`
  - `data/regression_checks/`
  - `data/audited_posts/`
  - `data/aggregated_stats/`
  - `data/narrative/`
  - `data/reports/`

- **Subagent Division of Labor (Multi-Agent Setup)**
  - **Infrastructure Agent (`infrastructure-agent`)**: Specializes in environment bootstrapping, dependency loading, client socket management, and timeframe calculation logic (`main.py`, `src/config_loader.py`, `src/report_period.py`).
  - **Classification Agent (`classification-agent`)**: Handles classification taxonomy support, catalog parsing filters, and structural regression checks (`src/classifier.py`, `src/auditor.py`, `src/regression_checks.py`, `src/classification_support.py`).
  - **Narrative/Report Agent (`narrative-agent`)**: Governs aggregated fact extraction, Uzbek text generation constraints, prefix validation, and in-place document healing (`src/narrative_generator.py`, `src/narrative_validator.py`, `src/report_generator.py`).

