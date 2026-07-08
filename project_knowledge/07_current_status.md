# Current Status

- **Current project stage**
  - End-to-end batch pipeline is implemented in the repository.
  - The repo contains the full weekly flow from Telegram ingestion to DOCX generation.
  - Current working state includes successful classification and audit validation artifacts for a real weekly run.

- **Implemented components**
  - Configuration loading from `config.yaml` with environment resolution.
  - `.env` loading at process start.
  - Report-period calculation in `Asia/Tashkent`.
  - Telegram session/authentication flow and weekly channel post extraction.
  - Exclusion of posts without substantive text.
  - Reference-data loading for:
    - classification specification
    - 24 issues dataset
    - 162 laws dataset
  - Gemini batch classification with structured output normalization.
  - Deterministic regression checks for classification outputs.
  - Gemini batch audit of all classified posts.
  - Deterministic regression checks for audited outputs.
  - Aggregation of audited posts into per-channel and system totals.
  - Fact-based Uzbek narrative generation.
  - Deterministic narrative validation.
  - Reference-DOCX-based report generation logic.
  - Persistent run artifact structure under `data/`.

- **Observed current artifacts**
  - Present:
    - `data/raw_posts/raw_posts.json`
    - `data/classified_posts/classified_posts.json`
    - `data/regression_checks/classification_regression_checks.json`
    - `data/audited_posts/audited_posts.json`
    - `data/regression_checks/audit_regression_checks.json`
    - `data/aggregated_stats/aggregated_stats.json`
    - `data/narrative/narrative.json`
  - Current validation state in stored artifacts:
    - classification checks passed for `1097` posts
    - audit checks passed for `1097` posts

- **Unfinished / not yet materialized in current repo state**
  - Baseline prior period reference features full support (modes: "auto", "explicit", "previous_week", "current_week"), though cross-period baselines are omitted if no prior-period file is attached.

- **Practical state summary**
  - The repository is fully implementation-complete, production-ready, and stabilized.
  - Recent upgrades:
    1. **Markdown References Ingestion:** Successfully migrated `24_ta_masala` and `Qonunlar_taqsimoti` references from `.docx` to `.md` format. Implemented context-bounded list item parsing and cell-isolated markdown table column parsing to eliminate parsing noise.
    2. **TTY Timeframe Selection Prompt:** Injected an interactive CLI prompt at `main.py` startup for user week selection (Joriy hafta / O'tgan hafta) with automated non-TTY fallback and interrupt handling.
    3. **In-place Prefix Healing:** Upgraded `validate_narrative` to auto-heal section formatting prefixes in-place instead of throwing destructive ValueErrors.
    4. **Verified Compilation:** Statically compiled all source files successfully.
