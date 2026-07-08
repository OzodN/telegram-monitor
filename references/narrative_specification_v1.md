# Narrative Generation Specification v1

This repository adopts `narrative_specification_v1.md` as the authoritative source of truth for weekly report commentary generation.

Operational rules implemented in code:

- Use only structured aggregation facts and deterministic precomputed values.
- Do not use raw Telegram post text for narrative generation.
- Do not invent causes, motives, trends, political interpretations, or missing facts.
- If required structured data is unavailable, omit the claim.
- Prohibited language includes: `ehtimol`, `aftidan`, `ko'rinishicha`, `bu shundan dalolat beradi`, `sababi shuki`.
- All numeric values in the narrative must match deterministic aggregation results.
- Trend language is prohibited when prior-period data is absent or the methodology version differs.
- The pipeline remains: Extraction -> Classification -> Regression Checks -> Audit -> Aggregation -> Narrative Generation -> Narrative Validation -> DOCX Generation.

This local file exists so the production project keeps a stable in-repo reference path. The authoritative business content was supplied externally as `narrative_specification_v1.md` and is reflected by the implementation and validation rules in this codebase.
