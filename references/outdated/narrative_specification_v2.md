# Narrative Generation Specification v2.0

Authoritative source of truth for weekly report narrative generation (Namangan region Kengash channel monitoring). Synced against `classification_specification_v3.md`.

## 0. Foundational Rules

- Use only structured aggregation facts and deterministic precomputed values.
- Do not use raw Telegram post text for narrative generation.
- Do not invent causes, motives, trends, political interpretations, or missing facts.
- If required structured data is unavailable, omit the claim — do not approximate.
- All numeric values in the narrative must exactly match deterministic aggregation results.
- Prohibited hedge language includes: `ehtimol`, `aftidan`, `ko'rinishicha`,
  `bu shundan dalolat beradi`, `sababi shuki`.

## 1. Mandatory Item Structure

Every category item must follow this four-part shape. An item that only states the
overall number without the remaining parts is incomplete and must not be emitted:

1. **Overall indicator** — the aggregate figure for the category.
2. **Leaders** — top-performing region(s)/channel(s) named explicitly, with exact number.
3. **Bottom/zero performers** — lowest or zero-performing region(s)/channel(s), named explicitly.
4. **Content description** — which topics, subjects, or issue types make up the figure.

## 2. Trend Language (revised)

- Trend language ("worsened compared to prior week," "improved compared to prior week") is
  **prohibited by default** when prior-period data is absent or the methodology version differs.
- **Exception:** for Categories 10–11 (work plan and its execution) specifically, when
  valid prior-period data under the same methodology *is* available, trend language is
  **required, not optional**, and should be stated with clear emphasis — this is a
  designated critical-oversight point in the source reporting standard.

## 3. Per-Category Rules

**Category 1 — Total posts (computed total).**
State the overall total. Name the highest- and lowest-activity regions with their exact
counts. If any channel had zero posts on specific date(s), name the channel and the
specific date(s) separately.

**Category 2 — Reposts / unrelated posts.**
Always state count together with percentage, in the form "X ta (Y%)." Describe which
regions it occurs in more frequently and its topical content (e.g., political initiatives,
general congratulatory posts). If any region/district shows literally 0% reposts, state
this as a positive finding, called out separately. List all zero-count regions in full,
or summarize concisely (e.g., "no reposts observed in 14 of 15 channels; only channel X
had Y instances").

**Category 3 — Leadership activity.**
Analyze the Hokim (governor), Kengash chairperson, and secretariat head **each
separately** — never as a combined figure. For each of the three: list every
district/city channel that covered them, as a full comma-separated list. In addition:
(a) explicitly identify any region where **none** of the three (neither Hokim, chair, nor
secretariat head) were covered; (b) if any single person accounts for an unusually large
share of a channel's coverage (e.g., over 50%), flag this as an anomaly in its own
statement.

**Category 4 — Article 24 inquiries/studies.**
Name leading and low-performing regions. Concretely enumerate which subject areas were
covered (education, medicine, social issues, employment, prices, culture, investment) —
do not summarize as "various issues."

**Category 5 — Deputy inquiries and their resolution.**
Treat "inquiry sent" and "inquiry resolved" as two distinct facts — analyze them
**separately**, never conflate a sent inquiry with a resolved one. Classify inquiries by
problem type per region (road, water, gas, electricity, social). Explicitly name any
region that sent **no inquiries at all**.

**Category 6 — Coverage of Law No. 162 [presidential decree/law reference].**
Name the leading region and any region(s) that do not cover this topic **at all**. Note:
this category has historically been under-developed relative to others (see Category 4
and 7 treatment) — it should receive the same depth of leader/zero-region comparison as
those categories, not just a listing of law names.

**Category 7 — Permanent commissions.**
Name the leading region, the internal (district-level) distribution, and any region(s)
**entirely uncovered**. Caution: example phrasings that may exist in prior drafts or
memory (e.g., "Chortoq, Namangan, Yangiqo'rg'on and Kosonsoy led") may not reflect the
current period's actual numbers — do not reuse such phrasing without verification. Any
region listed as "0"/uncovered must be re-checked against the actual current-period count,
since a nominal "0" may in fact be a small nonzero value (e.g., 1 post). **This category
carries the strictest verification requirement in the entire spec: no leader or
zero-coverage claim may be written until the underlying number has been confirmed against
the aggregation output for the current reporting period.**

**Category 8 — Expert/Youth group activity.**
This is typically the rarest category (~1–2% of volume). Because occurrences are rare,
describe in detail what was actually discussed in each instance that does occur (e.g.,
review of draft decisions, youth engagement activities, legal-culture initiatives) rather
than reducing it to a bare count.

**Category 9 — Sessions.**
List which regions held sessions and which did not. Enumerate the main issues discussed
in the sessions that did occur.

**Categories 10–11 — Work plan and its execution.**
Designated critical-oversight categories. Always name, explicitly, which regions are
lagging in this area. If an indicator is very low or near zero, emphasize this strongly.
Where valid same-methodology prior-period data exists, state the trend explicitly (see
Section 2 exception above).

**Category 12 — Other/miscellaneous matters.**
This category's contents are heterogeneous by nature — never report it as a single raw
number. Break it into the following six-value closed subtype schema and report each
present subtype with its count (and percentage of the Category 12 total, per Category 2's
established "X ta (Y%)" convention):

1. `template` — recurring, content-free announcements (channel greetings, social-media
   promotion invitations, generic schedule announcements) per classification Definition 2.9.
2. `legislative_news` — legal/legislative explainers, summaries, or announcements with no
   named individual performing a monitoring action, per classification Definition 2.1a(b).
3. `internal_organizational` — content about the Kengash institution's own structure,
   powers, duties, or internal organizational function, per classification Definition
   2.1a(c); this also covers personal work schedules/plans of the kotibiyat mudiri, a
   deputy, or a specialist that fail the Council-ownership test (classification
   Definition 2.7d), and deputy introduction/profile posts.
4. `press_article` — third-party press/media coverage of council-related matters that is
   not itself session coverage (session TV/media coverage is Category 9, not Category 12
   — see classification Category 9 Inclusion Criteria).
5. `unmatched_field_investigation` — genuine on-site investigative or monitoring activity
   (о'рганилди / study conducted) that fails to qualify for Categories 4, 6, or 7 solely
   on a technicality of actor type, list membership, or topic match — for example, a
   study of a topic structurally similar to but not on the 24-Issues list (classification
   EDGE-4.2), or a law-monitoring study of a law not on the 162/96 list (classification
   EDGE-6.1). This is distinct from `legislative_news`: the post describes a specific
   investigative act, not merely a legal explainer. **Cross-reference note:** as of
   classification specification v3.0, genuine on-site law-monitoring conducted by a
   kotibiyat mudiri or kotibiyat mutaxassisi is now Category 6 (not Category 12) per
   Section 0.2.1 of that spec — do not classify such posts as
   `unmatched_field_investigation`; only posts that fail Categories 4/6/7 for a genuine
   list/topic-membership reason belong in this subtype.
6. `other` — Category 12 content not matching any of the above five subtypes.

Reconcile this subtype list against the classification specification's Category 12
"Mandatory inclusions" list (Section 5, Category 12) before each generation run — if a
future classification spec version adds, removes, or redefines a mandatory-inclusion
type, this six-value schema must be updated to match before the affected report is
generated. *(The adding
`unmatched_field_investigation` and reconciling it against classification EDGE-4.2/EDGE-6.1
is complete. This subtype schema is not itself present as an explicit field in
`classified_posts.json`; see Section 8, Implementation Note, below.)*

## 4. Miscellaneous / Free-Form Band

A free-form band exists for notable, unique situations that do not fit any numbered
column — for example: one channel showing unusually high or low activity, cooperation
with an external organization, or a methodological/advisory visit. This band is **not**
limited to any single recurring example (e.g., cooperation with the "Madad" NGO is one
possible instance, not the definition of the band). Include any Kengash channel that
published posts about cooperation with an external organization such as "Madad," but do
not treat this band as exhausted once that one example is covered — scan for any other
qualifying unique event in the reporting period.

## 5. Style Rules

- **Pair every claim with specifics.** An exact number must always be paired with an
  exact name (region, channel, or person). Vague phrasing such as "in many regions" or
  "several channels" is prohibited — if a specific name/count cannot be sourced from
  aggregation data, omit the claim per Section 0.
- **Never hide negative or zero results.** Zero indicators, lack of activity, or
  uncovered regions must be actively surfaced and called out, not softened or omitted —
  this is the report's oversight function.
- **End on the fact, not a conclusion.** Every item must end with the factual statement
  itself — not a summary, evaluation, or recommendation. Avoid evaluative or emotional
  closing language.
- Continue to avoid the prohibited hedge words listed in Section 0.

## 6. Verification-Before-Generation Rule ("Golden Rule")

Before writing any "leader," "lowest," "zero," or "uncovered" claim for **any** category,
the agent must re-verify the claim against the actual current-period aggregation numbers.
Do not rely on assumption, memory, prior-report phrasing, or pattern-matched examples —
a single incorrect number undermines the credibility of the entire report. This
verification step is a precondition for emitting the claim, not a downstream validation
check; it applies in addition to (not instead of) the post-hoc numeric-match validation
already defined in Section 0.

## 7. Known Gaps / Open Items

- ~~Category 12 subtype schema requires reconciliation with classification
  specification~~ — See Section 3, Category 12, for the closed
  six-value schema.
- No further open items as of this writing. Any future classification specification
  change to Category 12's mandatory-inclusion list (or to any other category, if it
  changes what narrative-relevant data the aggregator exposes) should trigger a review of
  this file's Section 3 for consistency.

## 8. Implementation Note (non-normative)

This section is informational for the pipeline engineering team, not a narrative-generation
rule for the LLM agent.

`classified_posts.json` currently carries no explicit subtype field for Category 12 posts
— the six-value subtype schema in Section 3 is inferred downstream by the aggregator from
each post's `category_reason` / `matched_rule` text via heuristic matching. This is a
plausible source of subtype-count drift independent of any top-level category
misclassification, since free-text heuristic matching is inherently less reliable than an
explicit field. Consider having the classifier emit an explicit `category_12_subtype`
field (one of the six values in Section 3) directly on each Category 12 post, so the
aggregator no longer needs to re-derive it from free text. This is a pipeline/aggregator
enhancement, not a narrative-specification rule, and is noted here only because it
directly affects the reliability of the Category 12 breakdown this spec requires the
narrative agent to report.