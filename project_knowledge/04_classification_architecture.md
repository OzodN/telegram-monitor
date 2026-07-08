# Classification Architecture

- **Classification source of truth**
  - Sole authoritative taxonomy: `references/classification_specification_v2.md`
  - It supersedes prior category instruction documents.
  - It defines:
    - assignable categories
    - precedence hierarchy
    - deterministic decision tree
    - rule IDs `P1` through `P14`
    - validation requirements
    - regression requirements

- **Reference datasets**
  - `references/24_ta_masala.md`
    - Used as the closed 24-issues reference dataset.
    - Canonicalized into issue IDs `ISSUE_01` to `ISSUE_24`.
    - Ingested via context-bounded parsing (parsing terminates at notes/appendix separator block markers) and positive list item matching.
  - `references/Qonunlar_taqsimoti.md`
    - Used as the 162-laws reference dataset.
    - Canonicalized into law reference IDs.
    - Ingested via cell-isolated splitting of table rows and custom markdown formatting stripping.
  - These datasets support evidence matching, dataset references, validation, audit, aggregation, and reporting.
  - They do not replace the authoritative classification specification.

- **Classification flow**
  1. Load the authoritative classification specification text.
  2. Extract and canonicalize the 24-issues dataset.
  3. Extract and canonicalize the 162-laws dataset.
  4. Split Telegram posts into Gemini classification batches.
  5. Send each batch to Gemini with:
     - post text
     - authoritative classification specification
     - canonical issue catalog
     - canonical law catalog
  6. Receive structured classification decisions for every post.
  7. Normalize dataset references to canonical IDs.
  8. Persist structured classified posts.

- **Per-post classification output contract**
  - Required stable fields:
    - `category_id`
    - `category_reason`
    - `matched_rule`
    - `evidence`
    - `dataset_references`
  - Conditional stable fields:
    - `request_marker`
    - `category_3_official`
    - `category_5_subtype`
    - `category_5_problem_type`
    - `category_12_subtype`
  - Supported dataset namespaces:
    - `issues_24`
    - `laws_162`

- **Validation layer**
  - Deterministic regression checks run after classification and after audit.
  - Validation rules enforce:
    - category is in the approved assignable set
    - `matched_rule` is valid and category-consistent
    - `category_reason` is non-empty
    - `evidence` is non-empty
    - dataset names are valid
    - dataset reference IDs are canonical and present in the relevant catalog
  - Category-specific checks:
    - Category 4 requires at least one canonical `issues_24` reference
    - Category 5 requires `request_marker`
    - Category 3 requires `category_3_official`
    - Category 5 requires `category_5_subtype` and `category_5_problem_type`
    - Category 6 requires at least one canonical `laws_162` reference
    - Category 12 requires `category_12_subtype`

- **Audit layer**
  - Every classified post is re-audited.
  - Audit uses:
    - the same authoritative classification specification
    - the same issue catalog
    - the same law catalog
    - the current classification as input context
  - Audit outputs the same core classification fields plus:
    - `audit_status`
    - `audit_notes`
  - `audit_status` is stable-state constrained to:
    - `confirmed`
    - `corrected`

- **Classification source-of-truth hierarchy**
  1. `classification_specification_v2.md`
  2. Canonical issue and law catalogs as support datasets
  3. Deterministic validation rules
  4. Audit pass over the same taxonomy

- **Downstream usage of classification**
  - Aggregation consumes audited classifications as final structured input.
  - Category-specific breakdowns rely on classification metadata:
    - Category 3 by official
    - Category 4 by issue
    - Category 5 by subtype/problem type
    - Category 6 by law
    - Category 12 by subtype
  - Narrative generation does not classify directly; it uses aggregated outputs derived from audited classifications.
