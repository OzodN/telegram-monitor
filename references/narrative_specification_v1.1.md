# Narrative Generation Specification v1.1

Authoritative source of truth for weekly report narrative generation (Namangan region Kengash channel monitoring).

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
number. Break it into its component subtypes and report each (e.g., template posts,
general legislative news, internal-organizational matters, press articles, and any other
subtypes defined by the current classification specification). Reconcile subtype labels
against the classification specification's current Category 12 subtype schema before
generation — if the classification spec has added or renamed a subtype, this narrative
spec's subtype list must be updated to match before the affected report is generated.
*(Open item: as of this writing, reconciliation against classification spec v2.2's
EDGE-4.2/EDGE-4.4 labeling has not yet been completed — verify current subtype schema
before relying on this section.)*

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

- Category 12 subtype schema requires reconciliation with classification specification
  v2.2 (EDGE-4.2/EDGE-4.4) — see Section 3, Category 12 note.