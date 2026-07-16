# TELEGRAM MONITORING CLASSIFICATION SPECIFICATION
## Namangan Region Local Councils (Kengash) — Version 2.1

**Status:** AUTHORITATIVE.

**Applies to:** Human annotators, the Gemini classifier component, future auditors, regression test suites, and all validation tooling.

**Binding rule:** Every rule in this document is mandatory and non-optional. Where a rule appears to conflict with judgment or intuition, the rule in this document governs. There are no exceptions to Section 4 (Precedence Hierarchy) or Section 10 (Decision Tree).

---

## 0. DOCUMENT CONTROL

| Field | Value |
|---|---|
| Version | 2.1 |
| Category count | 12 (Category 1 is a computed total, not an assignable label) |
| Assignable categories | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| Number of categories per post | Exactly one category per post. No exceptions. |

---

## 1. PURPOSE AND SCOPE

This specification governs the classification of every Telegram post published by the 15 monitored Kengash (local council) channels in the Namangan region. Its purpose is to guarantee that **any two qualified classifiers — human or LLM — reading the same post and this specification will assign the identical category**, with zero discretionary judgment required.

This specification eliminates all ambiguity present in prior documents by:
- Defining every term used in category definitions in Section 2.
- Providing one deterministic decision procedure (Section 10) that every classification MUST follow, in order.
- Providing an explicit, total precedence ordering (Section 4) that resolves every possible overlap between categories.
- Providing explicit tie-breaking rules (Section 11) for every scenario where ambiguity cannot be eliminated by content alone.

---

## 2. CORE DEFINITIONS

These terms are used throughout this specification with the exact meaning defined here. No other interpretation is valid.

**2.1 Named Council Actor** — Any of the following, when identified by name, title, or explicit role reference in the post text:
- A sitting deputy of the Kengash (депутат / deputat)
- The hokim (ҳоким), when referenced in connection with council/deputy activity
- The Kengash raisi (кенгаш раиси / kengash raisi)
- The kotibiyat mudiri (котибият мудири / kotibiyat mudiri)
- A named secretariat specialist (котибият мутахассиси) or kotibiyat mudiri o'rinbosari (assistant/deputy secretariat head), acting on behalf of the Kengash
- A named standing committee (доимий комиссия / ДК)
- A named Expert Group or Youth Advisory Group

*Note: the kotibiyat mudiri o'rinbosari (assistant/deputy secretariat head) is a distinct role from the kotibiyat mudiri and is NOT one of the "three special officials" referenced throughout this specification (see 2.11). The o'rinbosari is treated as a regular secretariat specialist for all classification purposes.*

**2.1a Council-Related Subject Matter** — This definition governs the Category 2 / Category 12 boundary specifically (Gates P11 and P13, Section 4). It is broader than, and independent of, Definition 2.1: a post can satisfy 2.1a without containing any Named Council Actor at all. A post satisfies "Council-Related Subject Matter" if its substantive content concerns ANY of the following:

  (a) A Named Council Actor (2.1) is present — this subsumes the old test as one sufficient (but no longer necessary) condition.
  (b) The post explains, summarizes, announces, or references any law, legislative act, presidential decree, government resolution, legal right, or legal/regulatory procedure — regardless of whether a specific deputy or official is named as performing any monitoring activity. This is true whether or not the post carries a recognized recurring civic-education hashtag (e.g., `#162_qonun`, `#162_ta_qonun`, `#Qonunchilikdagi_yangiliklar`, `#Bilasizmi`, `#Qonun_mazmuni`, `#Qonunlar_bilan_tanishing`, `#Amal_qiling`, `#yodda_tuting`) — such hashtags are a strong confirming signal but their absence does not defeat this test if the substantive content is still legal/legislative in nature.
  (c) The post substantively concerns the Kengash institution's own structure, powers, duties, function, or internal organizational activity (e.g., "Mahalliy Kengashlarning fuqarolar oldidagi vazifalari," an internal meeting evaluating deputies' performance or request effectiveness), even when referenced generically ("mahalliy kengash," "deputat") rather than via a specifically named individual.
  (d) The post substantively concerns deputies' duties, responsibilities, ethics, or role in a generic, non-individually-named sense (e.g., `#deputat_vazifasi`, "deputat o'z vazifalarini vijdonan bajarishi kerak"), or explains how citizens can identify or contact their deputy (e.g., an E-Kengash portal promotion).
  (e) The post describes an investigative, informational, or civic-support activity conducted at the mahalla/community level on a governance-, social-protection-, or public-service-adjacent topic, even if no specific named actor performed it (e.g., an unattributed report of a mahalla polyclinic visit or mahalla banker study).

A post satisfying 2.1a is NEVER Category 2. It is Category 12, unless it independently matches a higher-priority gate (P1–P10) first — 2.1a is evaluated only at Gate P11, after all more specific categories have already been ruled out, and does not alter the boundaries of Categories 3–11 in any way.

Category 2 (Gate P13) is reserved exclusively for content that satisfies NONE of (a)–(e) above — i.e., content with no connection whatsoever to law, legislation, governance, or council/deputy institutional matters (for example, a purely patriotic or calendar greeting with no legal or institutional framing, or content entirely outside the civic/governmental domain).

**2.2 Formal Deputy Request ("so'rov")** — A post SHALL be treated as containing a Formal Deputy Request if and only if it contains one of the following textual markers (in any script — Cyrillic or Latin):
- "сўров юборилди" / "so'rov yuborildi"
- "депутатлик сўрови" / "deputatlik so'rovi"
- "сўровга биноан" / "so'roviga binoan"
- "сўров натижасида" / "so'rov natijasida"
- An explicit statement that a written request was addressed to a named organization or official, requesting specific action, OR an explicit statement that work was completed as a result of such an inquiry

A citizen complaint (мурожаат / murojaat) that is personally investigated by a deputy on-site, WITHOUT one of the above markers, is NOT a Formal Deputy Request.

**2.3 The 24 Issues** — A closed, fixed list of 24 monitoring topics assigned to individual deputies for constituency investigation. The full list is reproduced in **Appendix A**. A post satisfies "24-Issue Investigation" if and only if its primary subject matter matches one of the 24 items in Appendix A, or the post carries the hashtag `#24_masala` (or equivalent Cyrillic rendering `#24_та_масала`) or the tag `#24talik`.

**2.4 The 162 Assigned Laws** — A closed list of laws individually assigned to specific deputies for implementation monitoring, organized by standing committee. Structure reproduced in **Appendix B**. A post satisfies "162-Law Monitoring" if and only if it names one of the assigned laws (see Appendix B for the committee-organized subject index) AND names the deputy or official responsible for it, OR carries the hashtag `#162` or `#162_ta_qonun`.

**2.5 The 96 Committee Laws** — The subset of laws tracked collectively by standing committees (ДК) rather than individual deputies, per **Appendix B**. A post satisfies "Committee Law Monitoring" if the primary actor is a standing committee (not an individual deputy) and the subject matter is a law from Appendix B.

**2.6 Council Session** — A formal, scheduled plenary meeting of the Kengash with a published agenda, distinguished from committee meetings, work groups, or informal gatherings. This includes direct session content as well as media coverage and analytical follow-up of a session (see Category 9, Section 5).

**2.7 Published Work Plan** — A post satisfies "Published Work Plan" if and only if it meets ALL FOUR of the following conditions:
  (a) specifies a defined future time period (the coming week or month);
  (b) lists at least one specific, named task or activity to be performed;
  (c) assigns responsibility for at least one task to a named person or role;
  (d) **the plan belongs to the Kengash (Council) itself as an institution — NOT a personal work plan or schedule of the kotibiyat mudiri, an individual deputy, or a secretariat specialist.**

Condition (d) is an absolute, non-negotiable disqualifier: a post describing the personal schedule or individual work plan of the kotibiyat mudiri, a deputy, or a specialist — however specific — does NOT satisfy Definition 2.7 and cannot be Category 10, regardless of how conditions (a)–(c) are met.

Where a post is unambiguously the Council's own institutional plan (condition (d) clearly satisfied) but is only partially explicit about task specificity (b) or named responsibility (c), classifiers must still verify (b) and (c) are textually present per the Mandatory Conditions in Category 10 below; any resulting ambiguity in degree of detail is recorded as a quality-warning (Section 12, V7) for the analytical narrative rather than silently omitted, but does not on its own justify treating a post as Category 10 if (a), (b), or (c) is genuinely absent.

**2.8 Plan Execution Reference** — A post satisfies "Plan Execution Reference" if it explicitly ties reported activity to a previously published **Council** work plan, via the hashtag `#ish_reja_ijrosi` (or Cyrillic `#иш_режа_ижроси`) or explicit language such as "иш режаси ижросига кўра" / "reja bo'yicha" / "belgilangan topshiriqlar bo'yicha."

**This definition applies exclusively to execution of the Kengash's (Council's) own institutional work plan. If a post describes the work plan of the kotibiyat mudiri, an individual deputy, or a specialist, or describes execution/completion of such a personal plan, this Definition does NOT apply, and Category 11 (Section 5) must not be assigned on that basis — even if the post carries the `#ish_reja_ijrosi` hashtag.** Such posts are classified per their actual content under the applicable category (typically Category 4, 5, 6, or 12).

**2.9 Template Post** — A post consisting substantially of a recurring, content-free announcement, including but not limited to: channel greeting templates ("Assalomu alaykum, hurmatli kuzatuvchilar!"), social media promotion invitations ("Bizni ijtimoiy tarmoqlarda kuzatib boring"), and generic schedule announcements that fail the Published Work Plan test (2.7). **A post satisfying this definition is always assigned Category 12.**

**2.10 Madad NGO Content** — Any post referencing the "Madad" NNT (nodavlat notijorat tashkiloti) organization, in any context. **A post satisfying this definition is always assigned Category 12, with absolute top priority over every other rule in this specification (see Gate P1, Section 4).**

**2.11 Special-Official Activity** — Any activity performed personally by the hokim, kengash raisi, or kotibiyat mudiri (excluding the kotibiyat mudiri o'rinbosari, per 2.1) that is not otherwise captured by Definitions 2.2 (Formal Deputy Request), 2.4/2.5 (Law Monitoring), 2.6 (Council Session), 2.7 (Published Work Plan), or 2.8 (Plan Execution Reference). This includes, without limitation: 24-Issue investigations personally conducted by these three officials, constituency work, voter meetings, citizen receptions, field inspections, and administrative or executive field visits — **whether or not the post uses explicit deputy-role language such as "deputat sifatida."** The single documented exception is the vacant electoral district substitute-duty scenario (see EDGE-3.2 in Category 3, Section 5), which is classified under Category 4 instead, provided explicit deputy-role language is present.

---

## 3. GLOBAL PRINCIPLES

**G1.** Every post receives exactly one category. Multi-category assignment is prohibited.

**G2.** Classification is determined by matching the post against the Decision Tree in Section 10, in the exact order given. The first matching node determines the category. Do not skip ahead or evaluate nodes out of order.

**G3.** The presence of a Named Council Actor (2.1) is sufficient, but no longer necessary, to exclude Category 2. Definition 2.1 is required input for Gates P2–P10 (determining which of Categories 3–11 applies). The Category 2 / Category 12 boundary specifically (Gates P11, P13) is governed by the broader test in Definition 2.1a, which a post can satisfy without any Named Council Actor being present at all.

**G4.** Hashtags are authoritative signals and are checked before free-text interpretation at every relevant Decision Tree node. If a hashtag and the surrounding text conflict, the hashtag governs, unless the hashtag is objectively misapplied (e.g., `#24_masala` on a post with zero investigative content) — in which case Rule T-ARB-1 (Section 11) applies.

**G5.** The three special officials — hokim, kengash raisi, kotibiyat mudiri — are subject to the following mandatory routing rules, with no exceptions other than those explicitly documented in this specification:
   - Any activity by these officials that constitutes a **Formal Deputy Request (2.2)** is governed by **Category 5**, NOT Category 3.
   - Any activity by these officials that constitutes a **24-Issue Investigation (2.3)** is governed by **Category 3**, NOT Category 4.
   - All other activity by these officials not captured by Gates P1–P8 (Section 4) is governed by **Category 3**, per Definition 2.11.

**G6.** Category 12 is the terminal category for all council-related content not captured by Categories 3–11. It is NOT a first-choice category and must never be assigned before the Decision Tree has been fully evaluated through Categories 3–11.

**G7.** Cross-posted content: if the identical post is published independently on multiple monitored channels, each publication is classified independently and identically (same category on each channel), and each is counted as a separate post in that channel's statistics.

**G8.** Language: classification is performed identically regardless of whether the post is written in Uzbek Cyrillic, Uzbek Latin, or Russian. All keyword and hashtag matching in this specification applies across all three scripts/languages; Appendix C provides the canonical cross-script matching table.

**G9.** Media-only posts (image, video, or document with no substantive caption text): classify based on caption text if present. If no caption text exists, assign Category 12 and flag for human review (see Section 12).

**G10.** Every classification output MUST include a non-empty `category_reason` field of 1–2 sentences citing the specific textual evidence (keyword, hashtag, or actor) that determined the assignment. A classification with an empty `category_reason` is invalid output and must be rejected by the pipeline's validation layer.

---

## 4. PRECEDENCE HIERARCHY (ABSOLUTE ORDER)

This is a total ordering. Evaluate every post against these gates strictly in sequence. The first gate that matches determines the category; all subsequent gates are not evaluated.

| Order | Gate | Resulting Category | Rule ID |
|---|---|---|---|
| 1 | Post mentions Madad NGO (2.10) | 12 | P1 |
| 2 | Primary actor is a named standing committee (ДК) | 7 | P2 |
| 3 | Primary actor is a named Expert Group or Youth Advisory Group | 8 | P3 |
| 4 | Post is about an official Council Session (2.6), including TV/media coverage of a session and post-session analytical articles | 9 | P4 |
| 5 | Post is a Published Work Plan of the Council itself (2.7, including mandatory condition d) | 10 | P5 |
| 6 | Post contains a Formal Deputy Request, or documents work completed as a result of such an inquiry (2.2) | 5 | P6 |
| 7 | Post satisfies 162-Law Monitoring (2.4) or Committee Law Monitoring (2.5) with individual-deputy actor | 6 | P7 |
| 8 | Post has a Plan Execution Reference tied to the Council's own plan (2.8) | 11 | P8 |
| 9 | Actor is hokim, kengash raisi, or kotibiyat mudiri, performing any activity not captured by Gates P1–P8 — including 24-Issue Investigations personally conducted by these officials — except the vacant-electoral-district substitute-duty scenario (EDGE-3.2, which routes to Gate P10) | 3 | P9 |
| 10 | Post satisfies 24-Issue Investigation (2.3) by any deputy or kotibiyat mudiri o'rinbosari (assistant secretariat head — excludes the hokim, kengash raisi, and kotibiyat mudiri themselves, who are governed by Gate P9 per G5), or by the raisi/kotibiyat mudiri under the vacant-district substitute-duty exception | 4 | P10 |
| 11 | Post satisfies Council-Related Subject Matter (2.1a), no prior gate matched — includes a Named Council Actor being present, OR legislative/legal content, OR generic council/deputy-institutional content, OR mahalla-level governance-adjacent investigative content, even without any specifically named individual | 12 | P11 |
| 12 | Post is a Template Post (2.9) | 12 | P12 |
| 13 | Post fails Council-Related Subject Matter (2.1a) entirely — a purely patriotic/calendar greeting or content genuinely unrelated to law, governance, council, or deputy activity | 2 | P13 |
| 14 | None of the above (residual) | 12 | P14 |

**This table is identical in logic to the Decision Tree in Section 10 and is provided as a quick-reference summary. Section 10 is the authoritative, fully-specified version.**

---

## 5. CATEGORY SPECIFICATIONS

### CATEGORY 1 — Total Published Posts

**Purpose:** Aggregate control total. Not an assignable classification label.

**Validation rule:** `Category 1 = Category 2 + Category 3 + Category 4 + Category 5 + Category 6 + Category 7 + Category 8 + Category 9 + Category 10 + Category 11 + Category 12`

Any deviation from this identity indicates a pipeline aggregation defect and must halt report generation.

---

### CATEGORY 2 — Posts Not Directly Related to Council Activities

**Purpose:** Capture the narrow residual of content that has no connection whatsoever to law, legislation, governance, or the activity of this Kengash, its deputies, or its officials. This is a small residual category, not a general-purpose bucket for anything lacking a named individual.

**Inclusion criteria (ALL must be true):**
- The post fails Council-Related Subject Matter (Definition 2.1a) entirely — none of 2.1a's conditions (a)–(e) are satisfied.
- Gates P1–P12 in Section 4 have all been evaluated and did not match.
- The content is one of: a purely patriotic/calendar/historical-date greeting with no legal or institutional framing, a purely personal congratulatory message (e.g., a birthday greeting) with no legal or institutional framing, or content genuinely unrelated to law, governance, or council/deputy activity in any way.

**Exclusion criteria (ANY makes this NOT Category 2):**
- The post satisfies Council-Related Subject Matter (2.1a) — including, without limitation: any explanation, summary, or announcement of a law, legislative act, presidential decree, or legal procedure (regardless of whether a deputy is named); any content about the Kengash institution's own structure, powers, or duties; any content about deputies' duties or ethics in a generic sense; any content helping citizens identify or contact their deputy; or any unattributed mahalla-level governance-adjacent investigative or civic-support activity (→ Category 12 in every case).
- The post is a Template Post per Definition 2.9 (→ Category 12, per P12, which is checked before P13).
- The post describes, profiles, or introduces a named deputy (→ Category 12).
- The post is a daily or weekly digest summarizing multiple council activities (→ Category 12, per Rule T-EDGE-3 below).

**Mandatory conditions:** Gate P13 in the Decision Tree is reached only after confirming no earlier gate (P1–P12) matched, including P11 (the 2.1a check).

**Precedence interactions:** Category 2 is the lowest-priority substantive category. It is assigned only when every other category, including the broadened Category 12 catch-all conditions (2.1a subject matter, Template Posts, digests), has been explicitly ruled out.

**Examples (correctly Category 2):**
- "Tug'ilgan kuningiz muborak bo'lsin!" (birthday greeting, no legal or institutional content at all)
- A purely patriotic/historical greeting with zero legislative, legal, or institutional reference and no recurring channel template phrase (a genuinely rare case — see EDGE-2.1 below for the closely related case that is NOT this)
- Content entirely outside the civic/governmental domain (e.g., a weather notice with no connection to any council function) — not observed in the audited dataset, but the residual this category exists to capture

**Counterexamples (NOT Category 2):**
- "O'zbekiston Respublikasi Prezidentining PQ-98-son qarori qabul qilindi" (a presidential decree announcement) → **Category 12**, per 2.1a(b) — this is legislative content, regardless of whether a deputy is named.
- "#Qonunchilikdagi_yangiliklar ... Paxta-to'qimachilik sohasi korxonalari yanada qo'llab-quvvatlanadi" (a channel-branded legislative-news post about a presidential resolution) → Category 12, per 2.1a(b).
- "#162_qonun ... Mehnat kodeksi – xodim va ish beruvchi huquqlarining kafolati" (a generic Labor Code explainer with no deputy named) → Category 12, per 2.1a(b).
- "#deputat_vazifasi #yodda_tuting ... Deputat o'z vazifalarini vijdonan va halol bajarishi..." (a generic post about deputies' ethical duties, no individual named) → Category 12, per 2.1a(d).
- "Mahalliy Kengashlarning fuqarolar oldidagi asosiy vazifalari" (a post listing the Kengash institution's own general duties) → Category 12, per 2.1a(c).
- "Deputat mas'uliyati, so'rovlar natijadorligi va odob-axloq qoidalari tanqidiy tahlil qilindi... Xalq deputatlari Mingbuloq tumani Kengashida..." (an internal council meeting evaluating deputies' performance and request effectiveness, no individual named) → Category 12, per 2.1a(c) — this is genuine internal council organizational activity and must never default to Category 2 merely because no single deputy is named.
- "Kolgandaryo mahallasidagi 9-sonli oilaviy poliklinikada o'rganish ishlari olib borildi" (an unattributed report of a mahalla-level polyclinic investigation, no named investigator) → Category 12, per 2.1a(e).
- A "kunlik dayjest" aggregating the day's council posts → Category 12 (multi-activity digest, per Rule T-EDGE-3)
- "Assalomu alaykum, hurmatli kuzatuvchilar!" greeting template → Category 12 (Template Post, per P12)
- Same presidential decree news, but the post adds "Kengash deputati Sh. Ergashev bu qarorni ijro etish yuzasidan tushuntirish berdi" → Category 12 (named deputy present, 2.1a(a))

**Edge cases:**
- **EDGE-2.1:** A legal explainer post mentions a law from the 162-law list but names no deputy and describes no monitoring activity → **Category 12** (per 2.1a(b) — the absence of a named responsible deputy correctly disqualifies the post from Category 6, per Definition 2.4, but it does NOT default the post to Category 2; legislative/legal content is Council-Related Subject Matter regardless of deputy attribution).
- **EDGE-2.2:** A repost that quotes the hokim strictly in his executive (non-deputy, non-council) capacity, describing a purely municipal or ceremonial matter with no legislative content and no connection to Kengash business at all (e.g., attending a ribbon-cutting for a facility wholly outside any Kengash-tracked topic) → Category 2 is correct — this is the one hokim-related scenario that survives the 2.1a broadening, because it satisfies none of 2.1a(a)–(e).
- **EDGE-2.3:** A post carries a recurring channel civic-education hashtag (e.g., `#Bilasizmi`, `#162_qonun`) but the underlying content, on inspection, is not actually legal/legislative (e.g., the hashtag was applied to an unrelated announcement by mistake) → the hashtag is not itself dispositive; classify per the actual substantive content against 2.1a. If the actual content still fails all of 2.1a(a)–(e), Category 2 applies despite the hashtag's presence.

---

### CATEGORY 3 — Activities of Hokim, Kengash Raisi, and Kotibiyat Mudiri

**Purpose:** Track all activity personally performed by the three special officials — the hokim, kengash raisi, and kotibiyat mudiri — that is not already captured by a higher-priority gate. This includes constituency work, citizen receptions, field inspections, 24-Issue investigations conducted personally by these officials, and administrative/executive field visits.

**Inclusion criteria (ALL must be true):**
- The actor is the hokim, kengash raisi, or kotibiyat mudiri (NOT the kotibiyat mudiri o'rinbosari, per Definition 2.1), AND
- The activity is not captured by any of Gates P1–P8 (i.e., it is not a committee action, advisory group action, session content, Council work plan publication, Formal Deputy Request, 162-law monitoring with confirmed assignment, or Council Plan Execution Reference), AND
- The activity is not the vacant-electoral-district substitute-duty scenario described in EDGE-3.2 below.

**Exclusion criteria (ANY makes this NOT Category 3):**
- The activity is a Formal Deputy Request → Category 5 (Gate P6, evaluated before P9; per G5).
- The activity is captured by any of Gates P1–P8 for another reason (committee, advisory group, session, work plan, law monitoring, plan execution) → the corresponding category governs.
- The activity is the vacant-electoral-district substitute-duty scenario, with deputy-role language present → Category 4 (EDGE-3.2).

**Mandatory conditions:** The actor must be one of the three named officials. No explicit deputy-role language ("deputat sifatida") is required for this category — its presence or absence does not change the outcome, except in the specific vacant-district scenario of EDGE-3.2.

**Precedence interactions:** Category 3 is evaluated at Gate P9 — after Session (P4), Work Plan (P5), Formal Request (P6), Law Monitoring (P7), and Plan Execution (P8). Any post that matches an earlier gate is never evaluated for Category 3, even if one of the three special officials participates. Because Category 3 is evaluated before Category 4 (P10), any 24-Issue Investigation conducted personally by one of the three officials is captured here, at P9, and never reaches the Category 4 gate — this is the deliberate effect of G5.

**Examples (correctly Category 3):**
- "Kengash raisi R.Isakov saylov okrugida fuqarolar bilan uchrashuv o'tkazdi, ularning murojaatlarini tingladi" (voter meeting) → Category 3
- "Hokim, Kengash deputati B.Salimjonov o'z saylov okrugida fuqarolarni qabul qildi" (citizen reception) → Category 3
- "Kengash raisi R.Isakov tomonidan 32-sonli maktabgacha ta'lim tashkilotida sharoitlar o'rganildi" (a 24-Issue Investigation personally conducted by the raisi) → Category 3
- "Tuman hokimi X korxonasida ishlab chiqarish jarayoni bilan tanishdi" (administrative/executive-capacity visit, no deputy-role language) → Category 3

**Counterexamples (NOT Category 3):**
- "Kengash raisi tomonidan yo'l ta'mirlash bo'yicha tegishli tashkilotga so'rov yuborildi" → Category 5 (Formal Deputy Request, per Special Rule in Category 5 and per G5)
- "Deputat M.Rahimov (regular deputy, not one of the three officials) tomonidan 32-sonli maktabgacha ta'lim tashkilotida sharoitlar o'rganildi" → Category 4 (the actor is a regular deputy, not one of the three special officials, so G5's Category-3 routing does not apply)
- "ДК йиғилишида кенгаш раиси иштирокида масала кўриб чиқилди" (raisi participates in a standing committee meeting, but the committee is the primary actor) → Category 7 (Gate P2 precedes P9 absolutely)

**Edge cases:**
- **EDGE-3.1:** The kotibiyat mudiri conducts a field visit alongside the kengash raisi to inspect a factory, with no explicit deputy-role language present → **Category 3** (per the broadened scope of Definition 2.11; explicit deputy-role language is not required).
- **EDGE-3.2 (Vacant District Exception):** A vacant electoral district is temporarily served by the raisi or kotibiyat mudiri handling voter complaints on behalf of the vacant seat → **Category 4** applies, per the explicit provision in the source instructions for vacant-district coverage, **provided deputy-role language is present** in the post. If deputy-role language is absent in this scenario, the general Category 3 default (per Inclusion Criteria above) applies instead.

---

### CATEGORY 4 — Deputy Investigations Regarding the 24 Issues

**Purpose:** Track investigative field activity by regular deputies, the kotibiyat mudiri o'rinbosari, and secretariat specialists (i.e., all actors OTHER than the hokim, kengash raisi, and kotibiyat mudiri themselves) regarding the 24 officially monitored issues (Appendix A), plus the documented vacant-district exception for the three special officials.

**Inclusion criteria (ALL must be true):**
- The post describes an investigation, inspection, field visit, or study, AND
- The primary subject matches one of the 24 Issues in Appendix A, OR the post carries the `#24_masala` / `#24_та_масала` / `#24talik` hashtag, AND
- The actor is a regular deputy, a kotibiyat mudiri o'rinbosari, or a secretariat specialist — OR the actor is the raisi/kotibiyat mudiri acting under the vacant-electoral-district substitute-duty exception (EDGE-3.2) with deputy-role language present, AND
- The post does NOT contain a Formal Deputy Request marker (2.2) — if it does, Category 5 governs (Gate P6 precedes P10).

**Exclusion criteria (ANY makes this NOT Category 4):**
- The actor is the hokim, kengash raisi, or kotibiyat mudiri, acting outside the vacant-district exception → Category 3 (Gate P9 precedes P10, per G5).
- The post contains a Formal Deputy Request marker → Category 5.
- The post is primarily about a 162-assigned-law monitoring activity with a named responsible deputy, and does not independently match a 24-Issue topic → Category 6 (Gate P7 precedes P10).
- The primary actor is a standing committee (ДК), not an individual deputy → Category 7 (Gate P2 precedes P10 absolutely).
- The investigation is explicitly and genuinely a Plan Execution Reference tied to the **Council's own plan** (2.8) → Category 11 (Gate P8 precedes P10). Note per the example below: a hashtag alone does not satisfy this exclusion if the underlying content is an individual investigation, not Council-plan execution.

**Mandatory conditions:** At least one of the 24 Issues (Appendix A) must be identifiable as the primary subject, OR the explicit hashtag must be present. General-purpose "investigation" language without a matching 24-issue topic does not qualify.

**Precedence interactions:** Category 4 is evaluated at Gate P10 — the second-to-last substantive gate, after Session, Work Plan, Formal Request, Law Monitoring, Plan Execution, and Constituency/Special-Official Activity (Category 3) have all been ruled out.

**Examples (correctly Category 4):**
- "Deputat Sh.Erkinov tomonidan Yangi hayot MFYda ijtimoiy xodim faoliyati o'rganildi" (Issue #5 — social worker service quality; actor is a regular deputy) → Category 4
- Post tagged `#24_masala` describing investigation of market prices (Issue #10) by a regular deputy → Category 4
- "Kotibiyat mutaxassisi tomonidan mahalla bankiri faoliyati o'rganildi" (secretariat specialist investigating on Kengash's behalf, matches Issue #23 — employment) → Category 4
- An investigation explicitly tagged "`#ish_reja_ijrosi` bo'yicha o'tkazilgan tekshiruv" → **still Category 4**, because the content is an individual 24-Issue investigation, not execution of the Council's own institutional work plan (per the narrowed Definition 2.8); the hashtag alone does not convert it to Category 11.

**Counterexamples (NOT Category 4):**
- Same investigation post, but ending with "...natijasida tegishli tashkilotga so'rov yuborildi" → Category 5 (Formal Request marker present, Gate P6 governs)
- "ДК йиғилишида мактабгача таълим шароитлари муҳокама қилинди" (standing committee discussing the same topic) → Category 7 (committee actor, Gate P2 governs absolutely)
- "Kengash raisi tomonidan 32-sonli maktabgacha ta'lim tashkilotida sharoitlar o'rganildi" (actor is the raisi, not a regular deputy) → Category 3 (per G5)

**Edge cases:**
- **EDGE-4.1:** A citizen's complaint (murojaat) investigated on-site by a regular deputy, with no Formal Request marker → Category 4 (per Definition 2.2, an investigated complaint without a formal request marker does NOT qualify for Category 5).
- **EDGE-4.2:** A post investigates a topic not explicitly listed in the 24 Issues but structurally similar (e.g., internet connectivity in mahallas) → Category 12 (does not match Appendix A; absent the `#24_masala` hashtag, default to catch-all).
- **EDGE-4.3:** The `#24_masala` hashtag is present but the post content describes a session announcement with no investigative content → Rule T-ARB-1 (Section 11) applies: hashtag is disregarded as misapplied, and the post is classified per its actual content (likely Category 9).

---

### CATEGORY 5 — Deputy Requests and Their Results

**Purpose:** Track formal official requests sent by deputies (or by the kengash raisi/kotibiyat mudiri) to organizations, and the documented results of such requests.

**Inclusion criteria (post must satisfy A OR B):**
- **(A)** The post contains a Formal Deputy Request marker per Definition 2.2 — i.e., explicit language that a written request was sent to a named organization or official.
- **(B)** The post explicitly documents a result or completed action attributed to a prior request, using markers such as "so'rov natijasida," "so'roviga binoan," "deputat so'rovi asosida."

**Special Rule (mandatory):** Requests initiated by the Kengash raisi or kotibiyat mudiri belong to Category 5, not Category 3, regardless of any deputy-role language also present, and regardless of the G5 rule that otherwise routes these officials' 24-Issue Investigations to Category 3. Gate P6 is evaluated before Gate P9; this rule is automatically enforced by precedence order.

**Exclusion criteria (ANY makes this NOT Category 5):**
- The post describes only an investigation or citizen complaint handling, with no explicit request marker or result marker → Category 4 (regular deputy) or Category 3 (one of the three special officials), per Edge Case 4.1 and G5.
- A "result" post describes completed infrastructure work or resolved problems WITHOUT any explicit reference to a prior request → Category 4/3 (investigation-only, depending on actor) or Category 11 (if explicitly tied to a genuine Council Plan Execution Reference), NOT Category 5. A result cannot be assumed to originate from a request; the connection must be stated in the text.

**Mandatory conditions:** Either an explicit outbound request marker or an explicit result-of-request marker must be textually present. Silence on this point defaults the post out of Category 5.

**Precedence interactions:** Category 5 is evaluated at Gate P6 — before Law Monitoring (P7), Plan Execution (P8), and Special-Official Activity (P9). A request that also happens to concern a 162-assigned law, or that is made by the raisi/mudiri, is always Category 5 first.

**Examples (correctly Category 5):**
- "Yo'l ta'miri bo'yicha tuman yo'l xo'jaligiga rasmiy so'rov yuborildi" → Category 5
- "YO'L MUAMMOSI IJOBIY HAL QILINDI. Deputat so'roviga binoan mahalladagi yo'lning 300 metrli qismi ta'mirlandi." → Category 5 (explicit result-of-request marker)
- "Kengash raisi tomonidan elektr ta'minoti bo'yicha tegishli tashkilotga so'rov yo'llandi" → Category 5 (Special Rule; raisi as requester, overrides G5's Category-3 default)

**Counterexamples (NOT Category 5):**
- "Deputat fuqaro murojaatini joyida o'rganib chiqdi" (investigated, no request sent, no result stated) → Category 4
- "Ko'cha yoritilishi ta'mirlandi" (work completed, no request reference at all) → Category 4/3 or Category 11, depending on actor and whether a genuine Council Plan Execution Reference is present
- "Sayyor qabul samarasi: 5 ta muammo hal qilindi" without any "so'rov" language → Category 4 or 3, depending on actor (mobile reception results without documented formal requests)

**Edge cases:**
- **EDGE-5.1:** A post describes an investigation AND a request in the same paragraph → Category 5 always wins (per Gate P6 ordering; the presence of a request marker anywhere in the post text is sufficient, regardless of how much of the post is devoted to the investigation narrative).
- **EDGE-5.2:** A request is sent by a standing committee (not an individual deputy) → Category 7 governs (Gate P2 is absolute and precedes P6). Category 5's "requests" scope is limited to individual deputies, the raisi, and the kotibiyat mudiri — not committees.

---

### CATEGORY 6 — Monitoring Implementation of Assigned 162 Laws

**Purpose:** Track individual-deputy monitoring of the 162 laws formally assigned per Appendix B.

**Inclusion criteria (ALL must be true):**
- Deputies are attached to the law, and the post describes work carried out in the study of the implementation of that law, AND
- The post names a specific law from the 162-law list (Appendix B) OR carries the `#162` / `#162_ta_qonun` hashtag, AND
- A specific individual deputy (not a committee) is named as the actor performing the monitoring activity, AND
- The actor is confirmed (per Appendix B or the hashtag) to have this law's monitoring responsibility, AND
- The post does not contain a Formal Deputy Request marker (if it does, Category 5 governs per Gate P6, which precedes P7).

**Exclusion criteria (ANY makes this NOT Category 6):**
- The primary actor is a standing committee (ДК) → Category 7 (Gate P2 is absolute and always evaluated first).
- The post merely explains what a law says, with no named deputy performing a monitoring action → **Category 12**, always, per Definition 2.1a(b) (legal/legislative content is Council-Related Subject Matter regardless of whether a deputy is named).
- The post contains a Formal Deputy Request marker → Category 5.
- The post is a Plan Execution Reference for law-monitoring activity previously reported → apply Rule T-ARB-3 (Section 11): if the post is a first-time report of law monitoring, it is Category 6; if it explicitly frames the activity as reporting on execution of a previously published **Council's** plan item (not the deputy's or kotibiyat mudiri's own plan), it is Category 11.

**Mandatory conditions:** Both the law name (or hashtag) AND a named individual-deputy actor with confirmed assignment must be present. A law mention alone, without a confirmed responsible deputy, is insufficient.

**Precedence interactions:** Category 6 is evaluated at Gate P7 — after Session, Work Plan, and Formal Request gates, but before Plan Execution and Special-Official Activity.

**Examples (correctly Category 6):**
- "Deputat M.Rahimov 'Ijtimoiy sheriklik to'g'risida'gi qonunga biriktirilgan holda, tuman bandlik markazi faoliyatini o'rgandi" → Category 6
- Post tagged `#162` describing a deputy's field study of consumer credit law implementation at a bank branch → Category 6

**Counterexamples (NOT Category 6):**
- "Ijtimoiy sheriklik — hamkorlik va taraqqiyot omili" (explains what the law says, no deputy monitoring action) → **Category 12**, deterministically, per Definition 2.1a(b) — the distinction between "channel-authored" and "repost with no framing" that this counterexample no longer matters: legal/legislative content is Category 12 either way
- "ДК йиғилишида 'Экологик назорат тўғрисида'ги қонун ижроси муҳокама қилинди" (committee, not individual deputy) → Category 7
- Same law-monitoring post, but concluding with "...natijasida tegishli idoraga so'rov yuborildi" → Category 5

**Edge cases:**
- **EDGE-6.1:** A deputy monitors a law not on the 162-list but structurally similar in subject → Category 12 (does not satisfy Definition 2.4; the deputy is a Named Council Actor, so the post is not Category 2).
- **EDGE-6.2:** The `#162` hashtag is present but no deputy name or investigation content appears (e.g., a bare law-title announcement) → **Category 12** (per Rule T-ARB-1, the hashtag is treated as misapplied given zero monitoring-activity content, and the post defaults to Category 12 per Definition 2.1a(b) — bare law-related content is Council-Related Subject Matter regardless of deputy attribution).

---

### CATEGORY 7 — Standing Committee (ДК) Activities

**Purpose:** Track all activity where a named standing committee is the primary actor, including meetings, hearings, and monitoring of the 96 committee-tracked laws (Appendix B) — regardless of whether that law also appears on the 162-law individual-deputy list.

**Inclusion criteria (ALL must be true):**
- The primary actor is a named permanent standing committee (доимий комиссия / ДК), AND
- The post describes a committee meeting, hearing, investigation, or report.

**Exclusion criteria (ANY makes this NOT Category 7):**
- The commission named is a temporary commission (муваққат комиссия), such as the poverty-reduction temporary commission → Category 12 (per explicit rule; temporary commissions are never Category 7).
- The primary actor is an individual deputy, not the committee as a body → Category 4 or Category 6, depending on subject matter (or Category 3 if the individual is one of the three special officials, per G5).
- The post is about the Expert Group or Youth Advisory Group, not a standing committee → Category 8 (Gate P3).

**Mandatory conditions:** The committee must be explicitly named (e.g., "Маҳаллий бюджет ... доимий комиссияси") — a bare reference to "комиссия" without specifying which permanent committee does not qualify; verify against the five standing committees listed in Appendix B.

**Precedence interactions:** Category 7 is evaluated at Gate P2 — the second-highest priority gate in the entire hierarchy, superseding Categories 3, 4, 5, 6, 9, 10, and 11 whenever the committee is the primary actor. This absolute precedence exists because committee identity is an unambiguous, objectively verifiable signal that should never be overridden by subject-matter or actor-based categories.

**Examples (correctly Category 7):**
- "Маҳаллий бюджет, тадбиркорликни ривожлантириш ва иқтисодий ислоҳотлар масалалари бўйича доимий комиссия йиғилишида давлат-хусусий шериклик масалалари кўриб чиқилди" → Category 7
- "Коррупцияга қарши курашиш ва хавфсизлик масалалари бўйича доимий комиссия аъзолари ҳудудда ўрганиш ўтказди" → Category 7

**Counterexamples (NOT Category 7):**
- "Kambag'allikni qisqartirish bo'yicha muvaqqat komissiya yig'ilishi bo'lib o'tdi" (temporary commission) → Category 12
- "Doimiy komissiya a'zosi M.Ergasheva shaxsan mahallada tekshiruv o'tkazdi" (individual committee member acting alone, not the committee as a body) → Category 4 or Category 6, depending on subject

**Edge cases:**
- **EDGE-7.1:** A standing committee investigates a topic that is also one of the 24 Issues (Appendix A) → Category 7 still governs (Gate P2 precedes P10 absolutely; committee actor identity overrides topic-based categories).
- **EDGE-7.2:** The Regulations and Ethics Committee (Регламент ва одоб комиссияси), whose members also sit on other committees per the source rules, conducts joint activity → classify under whichever committee is explicitly named as conducting the activity in the post text.

---

### CATEGORY 8 — Expert Group and Youth Advisory Group Activities

**Purpose:** Track the rare activities of formally constituted Expert Groups (Ekspert maslahati guruhi) and Youth Advisory Groups (Yoshlar maslahati guruhi).

**Inclusion criteria (ALL must be true):**
- The post explicitly names a formally constituted Expert Group or Youth Advisory Group as the actor, AND
- The post describes a meeting, consultation, investigation, or recommendation issued by that group.

**Exclusion criteria (ANY makes this NOT Category 8):**
- The post is about youth in a general sense (a youth event, a youth employment announcement) without naming the formal advisory group → Category 12.
- The post is about a standing committee (ДК), not an advisory group → Category 7.

**Mandatory conditions:** The formal group name must be explicitly stated. General youth-related or expert-adjacent content without this explicit naming does not qualify.

**Precedence interactions:** Category 8 is evaluated at Gate P3, immediately after Category 7 (Gate P2), and supersedes all subject-matter categories (3, 4, 6, 9, 10, 11) whenever the named group is the primary actor.

**Examples (correctly Category 8):**
- "Yoshlar maslahat guruhi yig'ilishida davlat xizmatiga qabul qilish jarayonlari muhokama qilindi" → Category 8

**Counterexamples (NOT Category 8):**
- "Mahallada yoshlar bilan ishlash bo'yicha shtab faoliyati muvofiqlashtirildi" (general youth coordination, no named formal group) → Category 12

**Edge cases:**
- **EDGE-8.1:** A joint meeting of the Youth Advisory Group and a standing committee → Category 7 governs (Gate P2 precedes P3 in the ordering; committee identity takes priority when both are present).
- **EDGE-8.2 (Misapplied Group Hashtag):** The post carries the hashtag `#Yoshlar_maslahat_guruhi` or `#Ekspert_guruhi`, but no content describing the actual activity of that Youth Advisory Group or Expert Group appears in the text (e.g., the post is only tangentially adjacent to a related event). In this case the hashtag is considered to have been used incorrectly. The post is classified as **Category 12**, based on the presence of a Named Council Actor, rather than as Category 8.

---

### CATEGORY 9 — Council Sessions

**Purpose:** Track all content related to official Kengash plenary sessions — announcements, agendas, proceedings, decisions, preparation, media coverage, and analytical follow-up.

**Inclusion criteria (ANY qualifies):**
- Session announcement (upcoming session date, agenda)
- Session proceedings report (what happened during the session)
- Adopted decisions from a session
- Explicit session preparation content, including generic statements such as "navbatdagi sessiyaga tayyorgarlik" (preparation for the upcoming session)
- News, posts, and links to TV/media broadcasts of the session, via television or internet
- Further analytical or evaluative articles on the results of the session

**Exclusion criteria (ANY makes this NOT Category 9):**
- The post is a temporary or standing committee meeting, not a full plenary session → Category 7.
- The post discusses a TV broadcast or analytical theme with no connection whatsoever to any identifiable Kengash session (e.g., general civic-education TV programming unrelated to a specific session) → Category 12.

**Mandatory conditions:** The post must reference the Council's own plenary session — directly, via media coverage of it, or via analysis of its outcomes — as a distinct institutional event; not a committee meeting, not a Kengash raisi's individual field meeting.

**Precedence interactions:** Category 9 is evaluated at Gate P4 — after committee and advisory-group actor checks (P2, P3), but before Work Plan (P5), Formal Request (P6), and all subsequent gates. A session-related post (including its media coverage or analysis) always takes priority over any subject-matter category it might otherwise also touch (e.g., if the session agenda includes a 162-law item, the post is still Category 9, not Category 6).

**Examples (correctly Category 9):**
- "ХАЛҚ ДЕПУТАТЛАРИ НАМАНГАН ВИЛОЯТИ КЕНГАШИНИНГ ЙИГИРМА УЧИНЧИ СЕССИЯСИ БЎЛИБ ЎТАДИ" → Category 9
- "Navbatdagi sessiyaga tayyorgarlik doirasida kun tartibidagi masalalar aniqlashtirilmoqda" → Category 9
- "Kecha bo'lib o'tgan sessiya viloyat telekanalida yoritildi" (TV coverage of the session) → Category 9
- "Sessiyada qabul qilingan qarorlar tahlili: bir oy o'tib nima o'zgardi?" (post-session analytical piece) → Category 9

**Counterexamples (NOT Category 9):**
- A general civic-education TV segment on local governance, with no reference to any specific Kengash session → Category 12
- "ДК йиғилишида кун тартибидаги масала муҳокама қилинди" (a standing committee meeting, not a plenary session) → Category 7

**Edge cases:**
- None beyond the exclusion criteria above.

---

### CATEGORY 10 — Weekly and Monthly Council's Work Plans

**Purpose:** Track genuine publication of new, specific work plans belonging to the Kengash (Council) itself — used to assess Kengash transparency compliance. This category is strictly limited to the Council's own institutional plan and excludes any personal work plan of the kotibiyat mudiri, an individual deputy, or a specialist.

**Inclusion criteria (ALL must be true, per Definition 2.7):**
- Specifies a defined future time period, AND
- Lists at least one specific, named task or activity, AND
- Assigns responsibility to at least one named person or role, AND
- **The plan is explicitly the Council's (Kengash's) own institutional plan — not the personal schedule or work plan of the kotibiyat mudiri, an individual deputy, or a secretariat specialist.**

**Exclusion criteria (ANY makes this NOT Category 10):**
- The post describes only the personal daily schedule or individual work plan of the kotibiyat mudiri, a specialist, or a deputy (e.g., "kotibiyati bosh mutaxassislari kunlik ish grafigi asosida ishlar tashkil etiladi") → Category 12. This exclusion applies regardless of how specific the schedule is, per Definition 2.7(d): the head of the board secretariat (or any specialist/deputy) does not have a Council "work plan" in the sense required by this category — only the Council itself does.
- The post is primarily a report on past completed activity, even if it also mentions future tasks in passing → Category 11 (per Rule T-ARB-4 in Section 11, when a single post mixes past-review and future-planning content, apply the Primary Verb Test).
- The post is a session agenda (future meeting topics) rather than a work plan (future operational tasks) → Category 9.

**Mandatory conditions:** All four elements of Definition 2.7 must be textually verifiable, including condition (d) — the plan must be attributable to the Council itself. Absence of any one element disqualifies the post from Category 10. Where the Council-ownership condition (d) is clearly satisfied but the level of task/person detail is only partially explicit, classifiers record this as a quality-warning per Section 12 (V7) for the analytical narrative, rather than reclassifying the post, provided (a), (b), and (c) are still minimally identifiable in the text.

**Precedence interactions:** Category 10 is evaluated at Gate P5 — after Session (P4) but before Formal Request (P6) and all subsequent gates. A work plan is prioritized over Category 11 whenever a genuine ambiguity between "new plan" and "past execution" exists (Rule T-ARB-4).

**Examples (correctly Category 10):**
- "Kelgusi haftaga mo'ljallangan **Kengash** ish rejasi: 1) Kotibiyat mutaxassisi A.Yusupov — 15-mahallada aholi qabuli (Dushanba); 2) Deputat M.Qosimov — maktab holatini o'rganish (Chorshanba)" → Category 10 (a Council-level plan that assigns specific tasks to named persons)

**Counterexamples (NOT Category 10):**
- "Kotibiyat bosh mutaxassislari kunlik ish grafigi asosida ishlar tashkil etiladi" (this is the specialists' own personal schedule, not the Council's institutional plan; fails condition (d) regardless of any surface-level schedule language) → Category 12
- "O'tgan hafta bajarilgan ishlar hisoboti va kelgusi hafta uchun umumiy yo'nalishlar" where the "kelgusi hafta" portion has no named tasks or persons → Category 11 (primary content is the past-week report)

**Edge cases:**
- **EDGE-10.1:** A weekly planning meeting reviews the past week AND assigns specific new tasks with named persons for the coming week, in roughly equal proportion, and the plan is confirmed to be the Council's own → apply the Primary Verb Test (Rule T-ARB-4): if the post's opening and headline concern the NEW plan → Category 10; if they concern the COMPLETED work → Category 11.

---

### CATEGORY 11 — Execution of the Council's Work Plan

**Purpose:** Track reports of completed activity explicitly tied to a previously published work plan belonging to the Kengash (Council) itself. This category strictly excludes execution of any personal work plan or schedule of the kengash raisi, the kotibiyat mudiri, or an individual deputy/specialist.

**Inclusion criteria (ALL must be true):**
- The post carries a Plan Execution Reference per Definition 2.8 (explicit hashtag or explicit "reja bo'yicha" / "topshiriqlar bo'yicha" language), AND
- The post describes completed or in-progress activity (not a new plan announcement), AND
- **The plan being executed is the Council's own institutional plan.** Execution of the personal work of the kengash raisi, the kotibiyat mudiri, or an individual specialist/deputy does NOT qualify as Category 11, even if described using plan-execution language or the `#ish_reja_ijrosi` hashtag.

**Exclusion criteria (ANY makes this NOT Category 11):**
- No Plan Execution Reference marker is present, even if the activity described resembles routine work → classify per the applicable subject-matter category (typically Category 3, 4, 5, or 6).
- The post is a Formal Deputy Request result, explicitly tied to a request rather than a plan → Category 5 (Gate P6 precedes P8).
- The post is a new work plan publication, not an execution report → Category 10.
- The post is a multi-topic daily/weekly digest → Category 12 (Rule T-EDGE-3).
- The activity described is the personal work of the kengash raisi, kotibiyat mudiri, or an individual deputy/specialist, rather than the Council's collective plan → classify per the applicable category (typically Category 3 or 4), NOT Category 11.

**Mandatory conditions:** An explicit Plan Execution Reference marker (2.8) must be present, AND the execution must be attributable to the Council's own plan specifically. A general activity report without this marker, or one that only reflects an individual official's personal work, does not qualify for Category 11.

**Precedence interactions:** Category 11 is evaluated at Gate P8 — after Session, Work Plan, Formal Request, and Law Monitoring gates, but before Special-Official Activity (P9) and 24-Issue Investigation (P10). A post with a genuine Council-level Plan Execution Reference is always Category 11 even if its content would otherwise match Category 3, 4, or 6.

**Examples (correctly Category 11):**
- Post tagged `#ish_reja_ijrosi` describing completed pedestrian infrastructure work per the **Council's** published plan → Category 11
- "Reja bo'yicha belgilangan 3 ta topshiriqdan 2 tasi ijro etildi" → Category 11, **provided** this refers to the Council's own work plan. If the same statement instead describes the personal task completion of the kengash raisi, the kotibiyat mudiri, or an individual specialist/deputy, it is NOT Category 11 — classify per Category 3 or 4 instead.

**Counterexamples (NOT Category 11):**
- Same infrastructure work post, but with no plan-reference marker and instead stating "so'rov natijasida ta'mirlandi" → Category 5
- A one-off investigation report with no plan reference at all → Category 4 or Category 3, depending on actor
- An investigation explicitly tagged `#ish_reja_ijrosi` but which is, in substance, a personal 24-Issue investigation by an individual deputy (not Council-plan execution) → Category 4 (see Category 4 example above)

**Edge cases:**
- **EDGE-11.1:** A channel that never published a Category 10 work plan nonetheless posts content tagged `#ish_reja_ijrosi`, and the content is genuinely about the Council's collective execution activity (not an individual's personal work) → Category 11 still applies. The hashtag is a self-sufficient marker per Definition 2.8; Category 11 does not require independent verification that a corresponding Category 10 post exists in the same reporting period — but it does require that the underlying activity belongs to the Council, not to an individual official.

---

### CATEGORY 12 — Other Council-Related Issues

**Purpose:** The terminal catch-all for all council-related content not captured by Categories 3–11, and the mandatory home for specific content types identified below regardless of other content.

**Mandatory inclusions (always Category 12, checked at Gate P1 or P11/P12 per Section 4):**
- Any post mentioning Madad NNT (Gate P1, absolute top priority in the entire hierarchy — per Definition 2.10)
- Temporary commissions (муваққат комиссия), including the poverty-reduction commission
- Deputy introduction/profile posts
- Daily or weekly digest posts summarizing multiple different council activities (Rule T-EDGE-3)
- Template posts (greeting templates, social media promotion) per Definition 2.9
- Personal work schedules or individual work plans of the kotibiyat mudiri, a deputy, or a specialist, which fail the Council-ownership test in Definition 2.7(d)
- Any legal or legislative explanation, summary, or announcement — whether or not it names a Council Actor, and whether or not it carries a recognized civic-education hashtag — per Definition 2.1a(b)
- Any content about the Kengash institution's own structure, powers, duties, or internal organizational activity, per Definition 2.1a(c)
- Any content about deputies' duties, responsibilities, or ethics in a generic sense, or content helping citizens identify/contact their deputy, per Definition 2.1a(d)
- Any unattributed mahalla-level governance-adjacent investigative or civic-support activity, per Definition 2.1a(e)
- Misapplied group-specific hashtags per Edge Case 8.2

**Inclusion criteria (residual, per Gate P11):**
- The post satisfies Council-Related Subject Matter (Definition 2.1a) — via a Named Council Actor (2.1a(a)) OR any of 2.1a's broader conditions (b)–(e), AND
- No earlier gate (P1–P10) matched.

**Exclusion criteria:**
- If the post matches any earlier, more specific gate (P1–P10), that category governs instead.
- If the post fails Council-Related Subject Matter (2.1a) entirely, and none of the mandatory-inclusion conditions apply → Category 2.
- Session-related TV/media coverage and post-session analytical articles are NOT Category 12 — these are Category 9 (see Category 9, Inclusion Criteria).

**Mandatory conditions:** None beyond reaching this point in the Decision Tree without an earlier match.

**Precedence interactions:** Category 12 is evaluated last among the substantive gates (P11, P12), immediately before the final Category 2 gate (P13) and the residual fallback (P14). It is deliberately positioned so that it never pre-empts a more specific category.

**Examples (correctly Category 12):**
- "Deputat va siyosiy partiya hamkorligi. Sayfiddinova Umida Salaydinovna, 6-Uyg'ur saylov okrugidan deputat..." (deputy introduction) → Category 12
- Any post mentioning Madad NNT → Category 12
- "Kunlik dayjest: bugun kengash faoliyatida..." (multi-topic digest) → Category 12
- "Assalomu alaykum, hurmatli kuzatuvchilar!" → Category 12
- "Kotibiyat bosh mutaxassislari kunlik ish grafigi asosida ishlar tashkil etiladi" (personal specialist schedule, fails 2.7(d)) → Category 12
- "#162_qonun ... Ekologik nazorat — sog'lom atrof-muhit kafolati!" (a generic law explainer, no deputy named) → Category 12, per 2.1a(b)
- "O'z hududingiz deputati kimligini bilasizmi? E-kengash portali orqali..." (a portal promotion helping citizens find their deputy) → Category 12, per 2.1a(d)

**Counterexamples (NOT Category 12):**
- A digest post that describes only ONE specific activity type (e.g., exclusively Formal Deputy Requests sent that day) → classify per that specific activity's category (Category 5), not Category 12, because it is not multi-topic.
- "Kecha bo'lib o'tgan sessiya viloyat telekanalida yoritildi" → Category 9 (session TV coverage; NOT Category 12)

**Edge cases:**
- **EDGE-12.1:** A post satisfies the Mandatory Inclusion list (e.g., Madad NNT) but ALSO contains content matching an earlier gate (e.g., a Formal Deputy Request from Madad NNT to a Kengash official) → the Madad NNT mandatory rule (Gate P1) is absolute and always wins, per Section 4. This is an explicit, deliberate exception to the general specificity principle, adopted because Madad NNT tracking is a fixed reporting requirement.

---

## 6. GLOBAL EXCLUSION AND EDGE-CASE RULES (CROSS-CATEGORY)

**Rule T-EDGE-3 (Digest Posts):** Any post that functions as a digest, summary, or roundup covering more than one distinct activity type (e.g., an investigation AND a request AND a session mention in the same post) is classified as Category 12, regardless of the individual activities summarized within it. A digest covering only one activity type across multiple instances (e.g., five separate 24-Issue investigations, and nothing else) is classified per that single activity type (Category 4 in this example), not Category 12.

---

## 7. TIE-BREAKING RULES (SECTION 11)

These rules resolve residual ambiguity that content analysis alone cannot eliminate. They are arbitrary but fixed — once adopted, they must be applied identically every time.

**T-ARB-1 (Misapplied Hashtag Rule):** If a post carries a category-determining hashtag (`#24_masala`, `#162`, `#ish_reja_ijrosi`, `#Yoshlar_maslahat_guruhi`, `#Ekspert_guruhi`) but contains zero corresponding substantive content (e.g., `#24_masala` on a pure session announcement with no investigation described), the hashtag is disregarded and the post is classified per its actual textual content using the standard Decision Tree, skipping the gate the hashtag would have triggered.

**T-ARB-2 (Hokim/Raisi/Mudiri Activity Default):** Per G5 and Definition 2.11, any activity by the hokim, kengash raisi, or kotibiyat mudiri that is not captured by Gates P1–P8 defaults to Category 3, regardless of whether explicit deputy-role language ("deputat sifatida") is present. The sole documented exception is the vacant-electoral-district substitute-duty scenario (EDGE-3.2), where deputy-role language is required for the post to be routed to Category 4 instead.

**T-ARB-3 (First Report vs. Execution Report for Law Monitoring):** If a law-monitoring activity by an individual deputy is reported for the first time (no prior Category 10 plan explicitly referenced), it is Category 6. If the same post explicitly frames the activity as reporting on execution of a previously published **Council's** plan item (not the deputy's or kotibiyat mudiri's own plan), it is Category 11.

**T-ARB-4 (Primary Verb Test for Plan vs. Execution):** When a single post contains both a review of completed work and an announcement of new tasks in comparable proportion, and the plan/activity is confirmed to belong to the Council itself, classify based on which element appears first and is emphasized in the post's opening sentence and/or title. If genuinely balanced with no clear opening emphasis, default to Category 10 (plans take priority over execution for transparency-monitoring purposes, since compliance tracking of NEW plan publication is the higher-priority monitoring objective).

**T-ARB-5 (Multiple Simultaneous Actors):** If a post names both an individual deputy AND a standing committee as co-actors in the same activity, Category 7 governs (committee identity is absolute per Gate P2), unless the committee's involvement is merely incidental (e.g., "committee member M, acting individually, also occasionally attends committee sessions") — in which case classify per the individual deputy's activity.

**T-ARB-6 (Ambiguous Script/Language Matching):** All hashtag and keyword matching (Appendix C) must be performed case-insensitively and across Cyrillic/Latin script variants. If a post uses non-standard transliteration not covered by Appendix C, classifiers must apply phonetic equivalence matching before defaulting to "no match."

**T-ARB-7 (Unresolvable Residual Ambiguity):** In the rare case that a post cannot be resolved to a single category after applying the full Decision Tree and all T-ARB rules above, default to Category 12 and flag the post for mandatory human review (see Section 12). Category 12 is the specification's designated safe default; it must never be Category 2, Category 4, or Category 5 in cases of genuine unresolved ambiguity, because those categories carry specific compliance-tracking weight that a miscategorized ambiguous post would distort.

---

## 8. APPENDIX A — THE 24 ISSUES (AUTHORITATIVE, VERBATIM)

1. Маҳалладаги ёшлар етакчиси томонидан амалга оширилаётган тадбирлар самарадорлиги, ёшлар бандлиги.
2. Аҳолига ўз вақтида сифатли тиббий ёрдам кўрсатилиши ҳолати.
3. Маҳаллаларда аҳоли ва болалар учун спорт иншоотлари, умумтаълим мактаблари, колледж ва академик лицейларнинг спорт заллари ва улардаги спорт анжомлари мавжудлиги, уларнинг жиҳозлари ҳолати.
4. Ҳоким ёрдамчилари томонидан амалга оширилаётган ишлар самарадорлиги, хусусан аҳолини камбағалликдан чиқариш ишлари.
5. Маҳалладаги ижтимоий ходим томонидан аҳолининг ижтимоий эҳтиёжманд тоифаларига кўрсатиладиган хизматни сифатли ташкил этилиши, кам таъминланган оилаларга ижтимоий нафақалар ва моддий ёрдам тайинлаш ва тўлаш.
6. Маҳалла хотин-қизлар фаоли томонидан амалга оширилаётган ишлар самарадорлиги.
7. Маҳалладаги солиқ инспектори томонидан унга юклатилган масалаларни амалга оширилиши ҳолати.
8. Маҳалла ички кўча йўллари ҳолати, кўчаларни тунда ёритилиши, автомобиль йўлларидаги тирбандликлар, йўл транспорт ҳодисалари кўп содир бўлаётган жойларда ЙТҲларни камайтиришга қаратилган чора-тадбирлар.
9. Бепул бериладиган дорилар билан таъминлаш ҳолати.
10. Бозорлардаги аҳоли истеъмоли учун энг зарур маҳсулотлар нарх-навоси, маҳсулотларнинг етарлилиги.
11. Куз-қиш мавсумида иситиш тизими.
12. Лифтларни ишлаши.
13. Бошқарув компаниялари фаолияти самарадорлиги, кўп қаватли уйлар ички йўлаклари (подъездлари), ертўлалари, атрофидаги майдон тозалиги ва ёритилиши ҳолати.
14. Уйларда иссиқ ва совуқ сув билан таъминлаш, электр энергияси, газ билан боғлиқ масалалар.
15. Парклар, ҳиёбонлар, боғларнинг ҳолати.
16. Жамоат транспортининг мунтазам ҳаракатланиши, автобус бекатларининг ҳолати, чипталарни олишнинг қулайлиги.
17. Чиқиндиларни ўз вақтида олиб чиқиш ҳолати.
18. Ногиронлиги мавжуд шахсларга давлат томонидан берилган имтиёзларнинг тўғри қўлланилиши ҳолати.
19. Ҳудуддаги маданият муассасалари ва музейлар, кутубхоналар ҳолати.
20. Давлат хизматлари, ФҲДЁ органларида фуқароларга хизмат кўрсатилиши ҳолати.
21. Ҳудуддаги жиноятчиликка қарши кураш ҳолати, айниқса қизил ва сариқ ҳудудларда жиноятчиликни бартараф қилиш бўйича олиб борилаётган ишлар.
22. Ҳудуддаги инвестициялар бўйича ҳолат.
23. Аҳоли бандлиги масалалари.
24. Шу ойда сессияга киритиладиган масалаларни қоида тариқасида жойига чиқиб ўрганиш.

**Note:** Priority may be given to these issues from the standpoint of party affiliation and standing committee membership, per the source document's explanatory note. This does not change the classification rule — a match to any of the 24 items above qualifies for Category 4 (or Category 3, if personally conducted by the hokim/raisi/kotibiyat mudiri, per G5) regardless of the investigating deputy's party or committee affiliation.

---

## 9. APPENDIX B — LAW ASSIGNMENT REGISTRY (162 + 96 LAWS)

### 9.1 Laws Every Deputy Must Know (Baseline — not independently category-determining)

1. Ўзбекистон Республикаси Конституцияси тўғрисида (Конституциявий Қонун, №ЎРҚ-837, 01.05.2023)
2. Маҳаллий давлат ҳокимияти тўғрисида (Қонун, №913-XII, 02.09.1993)
3. Халқ депутатлари вилоят, туман ва шаҳар кенгаши депутатининг мақоми тўғрисида (Қонун, №706-II, 02.12.2004)
4. Маъмурий тартиб-таомиллар тўғрисида (Қонун, №ЎРҚ-457, 08.01.2018)
5. Норматив-ҳуқуқий ҳужжатлар тўғрисида (Қонун, №ЎРҚ-682, 20.04.2021)

*A post referencing only these five foundational laws, without deputy-specific monitoring activity, does not by itself trigger Category 6. Classify per standard rules (typically Category 2 or 12).*

### 9.2 Standing Committee Structure (Governs Category 6 vs. Category 7 Determination)

The 162 individually-assigned laws and the 96 committee-tracked laws are organized under five standing committees. The committee subject-area index below is the authoritative reference for matching law subject matter to the correct committee, for purposes of Category 7 actor verification and Category 6 assignment confirmation.

**Committee 1 — Маҳаллий бюджет, тадбиркорликни ривожлантириш ва иқтисодий ислоҳотлар масалалари бўйича доимий комиссия**
- Subject areas: Банк ва кредит соҳаси; Тадбиркорлик ва бюджет соҳаси; Транспорт, инвестициялар, валюта ва туризм соҳаси; Мулк ва рақобат соҳаси
- Example assigned laws: "Истеъмол кредити тўғрисида," "Тадбиркорлик фаолияти эркинлигининг кафолатлари тўғрисида," "Давлат-хусусий шериклик тўғрисида," "Риэлторлик фаолияти тўғрисида"

**Committee 2 — Коррупцияга қарши курашиш ва хавфсизлик масалалари бўйича доимий комиссия**
- Subject areas: Коррупцияга қарши курашиш ва мурожаатлар соҳаси; Хавфсизлик соҳаси; Фуқаролик жамияти соҳаси; Ҳуқуқбузарликлар профилактикаси, одам савдосига қарши курашиш соҳаси
- Example assigned laws: "Коррупцияга қарши курашиш тўғрисида," "Мурожаатлар тўғрисида," "Фуқаролик жамияти институтлари тўғрисида"

**Committee 3 — Фан, таълим ва соғлиқни сақлаш масалалари бўйича доимий комиссия**
- Subject areas: Илм-фан ва таълим соҳаси; Меҳнат ва ижтимоий ҳимоя соҳаси; Соғлиқни сақлаш соҳаси; Ёшлар ва спорт соҳаси; Гендер тенглиги соҳаси; Маданият ва маърифат соҳаси
- Example assigned laws: "Жисмоний тарбия ва спорт тўғрисида," "Таълим тўғрисида," "Соғлиқни сақлаш тўғрисида," "Гендер тенглиги тўғрисида"

**Committee 4 — Аграр, сув хўжалиги ва экология масалалари бўйича доимий комиссия**
- Subject areas: Қишлоқ хўжалиги соҳаси; Табиатни муҳофаза қилиш ва экологик назорат соҳаси; Сув хўжалиги ва озиқ-овқат хавфсизлиги соҳаси; Ер муносабатлари соҳаси; Қайта тикланувчи энергия ва коммунал хўжалик соҳаси; Ҳайвонот ва ўсимлик дунёси соҳаси
- Example assigned laws: "Экологик назорат тўғрисида," "Ер кодекси," "Сув ва сувдан фойдаланиш тўғрисида," "Кўп квартирали уйларни бошқариш тўғрисида"

**Committee 5 — Регламент ва одоб комиссияси**
- Cross-cutting: members of this committee also serve on other committees per source rule (categories_instruction, item 4) and receive law assignments accordingly. Classify per whichever specific committee is named as conducting the activity in the post text (per Edge Case 7.2).

**Reassignment rule:** If a committee member's deputy status is terminated, the kengash raisi and kotibiyat mudiri reassign that member's laws among the remaining committee members within 3 days. Classification is always based on the deputy named IN THE POST at the time of publication, not on the historical assignment record.

**Maintenance note:** The complete verbatim law-by-law assignment table (all ~162 individual entries and their designated deputies) is maintained as a living reference dataset, updated whenever committee membership or law assignments change. Classifiers (human or LLM) must cross-reference this dataset when a post names a specific law, to confirm subject-area alignment with the committee structure above. The dataset itself is not reproduced in full here because it changes independently of this specification's classification logic; only the structural rules governing its use are authoritative parts of this document.

---

## 10. DETERMINISTIC DECISION TREE (AUTHORITATIVE PROCEDURE)

Apply the following procedure to every post, in exact node order. Stop at the first node whose condition is TRUE and assign the indicated category. Do not evaluate subsequent nodes.

```
NODE 1 — Madad NNT Check
  Does the post mention "Madad" NNT in any context?
  → YES: ASSIGN CATEGORY 12. STOP.
  → NO: proceed to Node 2.

NODE 2 — Standing Committee Actor Check
  Is the primary actor a named permanent standing committee (ДК),
  per the five committees in Appendix B §9.2?
  (Apply T-ARB-5 if a committee AND an individual deputy are co-named.)
  → YES: ASSIGN CATEGORY 7. STOP.
  → NO: proceed to Node 3.

NODE 3 — Expert/Youth Advisory Group Actor Check
  Is the primary actor a named, formally constituted Expert Group
  or Youth Advisory Group, with substantive content describing its
  activity (apply EDGE-8.2 if the hashtag is present without content)?
  → YES: ASSIGN CATEGORY 8. STOP.
  → NO: proceed to Node 4.

NODE 4 — Council Session Check
  Does the post concern an official Kengash plenary session — its
  announcement, agenda, proceedings, decisions, preparation language,
  TV/media broadcast coverage, or post-session analytical follow-up —
  per Definition 2.6 and Category 9's Inclusion Criteria?
  → YES: ASSIGN CATEGORY 9. STOP.
  → NO: proceed to Node 5.

NODE 5 — Published Work Plan Check
  Does the post satisfy ALL FOUR elements of Definition 2.7
  (future period + specific task + named responsible person +
  the plan belongs to the Council itself, not an individual)?
  If the post mixes past-review and future-planning content,
  apply Rule T-ARB-4 (Primary Verb Test) to decide.
  → YES: ASSIGN CATEGORY 10. STOP.
  → NO: proceed to Node 6.

NODE 6 — Formal Deputy Request Check
  Does the post contain a Formal Deputy Request marker (Definition 2.2)
  — either an outbound request or an explicit result-of-request marker?
  → YES: ASSIGN CATEGORY 5. STOP.
  → NO: proceed to Node 7.

NODE 7 — 162-Law / Individual-Deputy Monitoring Check
  Does the post name a law from Appendix B (or carry #162/#162_ta_qonun)
  AND name a specific individual deputy with confirmed assignment
  responsibility for that law?
  Apply T-ARB-1 if hashtag present but content absent.
  → YES: ASSIGN CATEGORY 6. STOP.
  → NO: proceed to Node 8.

NODE 8 — Plan Execution Reference Check
  Does the post carry a Plan Execution Reference marker (Definition 2.8
  — #ish_reja_ijrosi or equivalent language), AND is the activity
  genuinely the Council's own institutional plan execution (NOT the
  personal work of the kengash raisi, kotibiyat mudiri, or an
  individual deputy/specialist)?
  Apply T-ARB-3 if the post could also be a first-time Cat 6 report.
  → YES: ASSIGN CATEGORY 11. STOP.
  → NO: proceed to Node 9.

NODE 9 — Special-Official Activity Check
  Is the actor the hokim, kengash raisi, or kotibiyat mudiri
  (not the o'rinbosari/assistant), AND is this NOT the vacant-district
  substitute-duty scenario with deputy-role language present (EDGE-3.2)?
  (Per G5, this includes 24-Issue investigations personally conducted
  by these three officials — no deputy-role language is required.)
  → YES: ASSIGN CATEGORY 3. STOP.
  → NO: proceed to Node 10.

NODE 10 — 24-Issue Investigation Check
  Does the post describe an investigation/inspection/study whose
  primary subject matches one of the 24 Issues (Appendix A), OR
  carry the #24_masala hashtag with corresponding content, performed
  by a regular deputy, a kotibiyat mudiri o'rinbosari, a secretariat
  specialist, or the raisi/kotibiyat mudiri under the vacant-district
  exception (EDGE-3.2, with deputy-role language present)?
  Apply T-ARB-1 if hashtag present but content absent.
  → YES: ASSIGN CATEGORY 4. STOP.
  → NO: proceed to Node 11.

NODE 11 — Council-Related Subject Matter Check
  Does the post satisfy Council-Related Subject Matter, Definition 2.1a —
  i.e., is ANY of the following true?
    (a) A Named Council Actor (Definition 2.1) is present as an actor,
        participant, author, or subject; OR
    (b) The post explains, summarizes, announces, or references any law,
        legislative act, presidential decree, government resolution, legal
        right, or legal/regulatory procedure — regardless of whether a
        deputy is named or a civic-education hashtag is present; OR
    (c) The post substantively concerns the Kengash institution's own
        structure, powers, duties, or internal organizational activity,
        even referenced generically; OR
    (d) The post substantively concerns deputies' duties, responsibilities,
        or ethics in a generic sense, or helps citizens identify/contact
        their deputy; OR
    (e) The post describes an investigative, informational, or
        civic-support activity at the mahalla/community level on a
        governance- or public-service-adjacent topic, even if unattributed.
  → YES (any of a–e): ASSIGN CATEGORY 12. STOP.
  → NO (none of a–e apply): proceed to Node 12.

NODE 12 — Template Post Check
  Is this a recurring Template Post per Definition 2.9
  (greeting, social media promotion, generic schedule)?
  → YES: ASSIGN CATEGORY 12. STOP.
  → NO: proceed to Node 13.

NODE 13 — Final Fallback
  The post fails Council-Related Subject Matter (2.1a) entirely and is not
  a template post (e.g., a purely patriotic/calendar greeting, a purely
  personal congratulatory message, or content genuinely unrelated to law,
  governance, or council/deputy activity in any way).
  ASSIGN CATEGORY 2. STOP.
```

**This decision tree is exhaustive.** Every post reaches a terminal assignment at exactly one node. No post can pass through all 13 nodes without receiving a category, because Node 13 is an unconditional final assignment.

---

## 11. VALIDATION & REGRESSION TEST REQUIREMENTS

Every classifier output (human or LLM) MUST be validated against the following before acceptance into the pipeline:

**V1.** `category_reason` field is non-empty and cites specific textual evidence (per Global Principle G10).

**V2.** Category assignment is one of {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}. No other value permitted.

**V3.** If category = 6 or 7, the `category_reason` must name the specific law or committee referenced, cross-checked against Appendix B.

**V4.** If category = 4, the `category_reason` must identify which of the 24 Issues (Appendix A, numbered 1–24) the post matches, or cite the `#24_masala` hashtag, and must confirm the actor is not one of the three special officials (unless the vacant-district exception applies).

**V5.** If category = 5, the `category_reason` must quote or paraphrase the specific Formal Deputy Request marker found in the post.

**V6.** Aggregation identity check: `Category 1 (total) = SUM(Categories 2–12)` for every channel and for the overall report. Any mismatch halts pipeline execution.

**V7.** Quality-warning flags (to be surfaced in aggregated output, not silently discarded):
   - Any post where Category 5 was assigned via Test B (result marker) without a corresponding Category 5 request post from the same deputy in the same or prior reporting period, for manual spot-check.
   - Any post where a hashtag was disregarded per Rule T-ARB-1.
   - Any post assigned via T-ARB-7 (unresolvable residual ambiguity) for mandatory human review.
   - Any Category 10 post where the Council-ownership condition (2.7d) is satisfied but task/person specificity (2.7b/c) is only marginally explicit, per the note in Category 10's Mandatory Conditions.
   - Per-channel ratio check: if Category 5 count exceeds 40% of (Category 4 + Category 5 + Category 3) combined for any channel, flag for manual audit of the Cat 4/Cat 5/Cat 3 boundary application.

**V8.** Regression test suite: a fixed set of at least 50 representative posts (drawn from Section 5's Examples and Counterexamples across all categories) must be maintained as a golden dataset. This set MUST include, at minimum, the 8 examples of Category 12 — legal explainers without a named deputy, generic deputy-duty content, Kengash-institutional-function content, and unattributed mahalla-level investigative content. Any classifier update (prompt change, model change) must reproduce the documented category for 100% of golden-dataset posts before deployment.

**V9.** Category 2 volume check: if Category 2 exceeds 5% of total classified posts for any reporting period, this is treated as a strong signal of a recurrence of the defect described in Section 0.1, and triggers mandatory human review of a sample of that period's Category 2 assignments before the report is finalized. This threshold is set well above the expected steady-state residual (~1–3%) specifically to catch regressions early rather than only after a full audit.

---

## 12. SUPERSESSION STATEMENT

This document is the sole and complete authoritative source for classification of Telegram posts in this monitoring pipeline.