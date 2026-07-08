from __future__ import annotations

import re
from dataclasses import dataclass

from src.models import DatasetReference, PathsConfig
from src.utils import read_utf8_text


ALLOWED_CATEGORIES = set(range(2, 13))
TREND_CATEGORIES = {10, 11}
ALLOWED_MATCHED_RULES = {f"P{index}" for index in range(1, 15)}
ALLOWED_DATASET_NAMES = {"issues_24", "laws_162"}
CATEGORY_ALLOWED_RULES = {
    2: {"P13"},
    3: {"P9"},
    4: {"P10"},
    5: {"P6"},
    6: {"P7"},
    7: {"P2"},
    8: {"P3"},
    9: {"P4"},
    10: {"P5"},
    11: {"P8"},
    12: {"P1", "P11", "P12", "P14"},
}
ISSUE_REFERENCE_PATTERN = re.compile(r"^ISSUE_(0[1-9]|1[0-9]|2[0-4])$")

QUOTE_TRANSLATION = str.maketrans(
    {
        "\u00a0": " ",
        "«": '"',
        "»": '"',
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "’": "'",
        "‘": "'",
        "ʼ": "'",
        "ʻ": "'",
        "`": "'",
        "´": "'",
        "–": "-",
        "—": "-",
        "‑": "-",
        "−": "-",
    }
)

CYRILLIC_TO_LATIN = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Е": "E",
    "Ё": "YO",
    "Ж": "J",
    "З": "Z",
    "И": "I",
    "Й": "Y",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "X",
    "Ц": "S",
    "Ч": "CH",
    "Ш": "SH",
    "Щ": "SH",
    "Ъ": "",
    "Ы": "I",
    "Ь": "",
    "Э": "E",
    "Ю": "YU",
    "Я": "YA",
    "Ў": "U",
    "Қ": "Q",
    "Ғ": "G",
    "Ҳ": "H",
}

CYRILLIC_TO_LATIN_TEXT = {
    **CYRILLIC_TO_LATIN,
    "Ў": "O'",
    "Ғ": "G'",
}

UZBEK_WORD_NORMALIZATION = (
    (r"\bto['’`´]g['’`´]risida\b", "togrisida"),
    (r"\bto['’`´]lov\b", "tolov"),
    (r"\bo['’`´]zbekiston\b", "ozbekiston"),
    (r"\bo['’`´]zini\b", "ozini"),
    (r"\bbyudjet\b", "budjet"),
)


def clean_markdown_syntax(text: str) -> str:
    # Remove HTML line breaks
    text = re.sub(r"<br\s*/?>", " ", text)
    # Remove markdown link syntax [Text](URL) -> Text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Strip markdown emphasis (*, _, **)
    text = re.sub(r"[*_`#]", "", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass(slots=True, frozen=True)
class ReferenceEntry:
    dataset: str
    reference_id: str
    title: str
    aliases: tuple[str, ...]
    source_text: str


@dataclass(slots=True)
class ReferenceCatalog:
    dataset: str
    entries: list[ReferenceEntry]
    prompt_text: str
    _entries_by_id: dict[str, ReferenceEntry]
    _alias_to_reference_id: dict[str, str]
    _normalized_aliases_by_reference_id: dict[str, tuple[str, ...]]

    def contains_reference_id(self, reference_id: str) -> bool:
        return reference_id.strip().upper() in self._entries_by_id

    def resolve(self, raw_reference: str) -> ReferenceEntry | None:
        candidate = raw_reference.strip()
        if not candidate:
            return None

        direct_id = candidate.upper()
        if direct_id in self._entries_by_id:
            return self._entries_by_id[direct_id]

        normalized = normalize_reference_text(candidate)
        resolved_id = self._alias_to_reference_id.get(normalized)
        if resolved_id is not None:
            return self._entries_by_id[resolved_id]

        containment_matches = [
            reference_id
            for reference_id, aliases in self._normalized_aliases_by_reference_id.items()
            if any(normalized in alias or alias in normalized for alias in aliases)
        ]
        unique_matches = list(dict.fromkeys(containment_matches))
        if len(unique_matches) != 1:
            return None
        return self._entries_by_id[unique_matches[0]]


@dataclass(slots=True)
class ClassificationReferenceData:
    classification_specification_text: str
    issues_24_text: str
    laws_162_text: str
    issues_24_catalog: ReferenceCatalog
    laws_162_catalog: ReferenceCatalog

    def catalog_for_dataset(self, dataset: str) -> ReferenceCatalog | None:
        if dataset == "issues_24":
            return self.issues_24_catalog
        if dataset == "laws_162":
            return self.laws_162_catalog
        return None


def load_classification_reference_data(paths: PathsConfig) -> ClassificationReferenceData:
    issues_24_text = read_utf8_text(paths.issues_24_md)
    laws_162_text = read_utf8_text(paths.laws_162_md)

    return ClassificationReferenceData(
        classification_specification_text=read_utf8_text(paths.classification_specification_md),
        issues_24_text=issues_24_text,
        laws_162_text=laws_162_text,
        issues_24_catalog=_build_issues_catalog(issues_24_text),
        laws_162_catalog=_build_laws_catalog(laws_162_text),
    )


def canonicalize_dataset_references(
    raw_references: list[dict],
    reference_data: ClassificationReferenceData,
) -> list[DatasetReference]:
    canonicalized: list[DatasetReference] = []

    if not isinstance(raw_references, (list, tuple, set)):
        return canonicalized

    for reference in raw_references:
        if not isinstance(reference, dict):
            continue
        dataset = str(reference.get("dataset", "")).strip()
        reference_id = str(reference.get("reference_id", "")).strip()
        if not dataset and not reference_id:
            continue

        catalog = reference_data.catalog_for_dataset(dataset)
        resolved_reference = catalog.resolve(reference_id) if catalog and reference_id else None
        canonicalized.append(
            DatasetReference(
                dataset=dataset,
                reference_id=resolved_reference.reference_id if resolved_reference else reference_id,
            )
        )

    return canonicalized


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.translate(QUOTE_TRANSLATION)).strip().casefold()


def normalize_reference_text(value: str) -> str:
    normalized = normalize_text(value)
    normalized = normalized.replace('"', " ")
    normalized = normalized.replace("'", "")
    normalized = re.sub(r"[().,:;!?/\\|]+", " ", normalized)
    normalized = re.sub(r"\s+-\s+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    for pattern, replacement in UZBEK_WORD_NORMALIZATION:
        normalized = re.sub(pattern, replacement, normalized)

    return normalized


def _build_issues_catalog(raw_text: str) -> ReferenceCatalog:
    entries: list[ReferenceEntry] = []
    list_item_pattern = re.compile(r"^\s*(\d+)\)\s+(.+)$")
    footnote_link_pattern = re.compile(r"\[\d+\]\(#footnote(?:-ref)?-\d+\)")

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Context-Bounding: stop parsing immediately at separator markers
        normalized_line = line.translate(QUOTE_TRANSLATION).casefold()
        if "изоҳ:" in normalized_line or "izoh:" in normalized_line or line.startswith("---"):
            break

        match = list_item_pattern.match(line)
        if not match:
            continue

        item_num = int(match.group(1))
        raw_title = match.group(2).strip()
        clean_title = footnote_link_pattern.sub("", raw_title).strip()

        if not (1 <= item_num <= 24):
            continue

        reference_id = f"ISSUE_{item_num:02d}"
        title = _clean_reference_title(clean_title)
        aliases = _build_aliases(title, extra_aliases=[reference_id])
        entries.append(
            ReferenceEntry(
                dataset="issues_24",
                reference_id=reference_id,
                title=title,
                aliases=aliases,
                source_text=line,
            )
        )

    entries.sort(key=lambda e: e.reference_id)
    seen_ids = [e.reference_id for e in entries]
    expected_ids = [f"ISSUE_{i:02d}" for i in range(1, 25)]
    if seen_ids != expected_ids:
        raise ValueError(
            f"issues_24 dataset must contain exactly 24 sequential entries (ISSUE_01 to ISSUE_24).\n"
            f"Found {len(seen_ids)} entries: {seen_ids}"
        )

    return _build_catalog("issues_24", entries)


def _build_laws_catalog(raw_text: str) -> ReferenceCatalog:
    entries: list[ReferenceEntry] = []
    seen_titles: set[str] = set()
    seen_ids: set[str] = set()

    for line in raw_text.splitlines():
        candidate = line.strip()
        if not candidate.startswith("|") or not candidate.endswith("|"):
            continue

        parts = [p.strip() for p in candidate.split("|")]
        if len(parts) < 3:
            continue

        raw_cell = parts[2]
        if not raw_cell:
            continue

        # Isolate split cells to prevent metadata leakage before stripping markdown
        cleaned_cell = clean_markdown_syntax(raw_cell)
        title = _extract_law_title(cleaned_cell)
        if title is None:
            continue

        normalized_title = normalize_reference_text(title)
        if normalized_title in seen_titles:
            continue

        reference_id = _build_law_reference_id(title, cleaned_cell)
        if reference_id in seen_ids:
            reference_id = f"LAW_{_slugify_reference_fragment(title)}"
        if reference_id in seen_ids:
            continue

        seen_titles.add(normalized_title)
        seen_ids.add(reference_id)
        aliases = _build_aliases(title, extra_aliases=_build_law_alias_candidates(title))
        entries.append(
            ReferenceEntry(
                dataset="laws_162",
                reference_id=reference_id,
                title=title,
                aliases=aliases,
                source_text=candidate,
            )
        )

    if not entries:
        raise ValueError("laws_162 dataset parsing produced no law entries")

    return _build_catalog("laws_162", entries)


def _build_catalog(dataset: str, entries: list[ReferenceEntry]) -> ReferenceCatalog:
    entries_by_id = {entry.reference_id.upper(): entry for entry in entries}
    alias_counts: dict[str, int] = {}
    normalized_aliases_by_reference_id: dict[str, tuple[str, ...]] = {}

    for entry in entries:
        entry_aliases: list[str] = []
        for alias in entry.aliases:
            normalized_alias = normalize_reference_text(alias)
            if not normalized_alias:
                continue
            entry_aliases.append(normalized_alias)
            alias_counts[normalized_alias] = alias_counts.get(normalized_alias, 0) + 1
        normalized_aliases_by_reference_id[entry.reference_id] = tuple(dict.fromkeys(entry_aliases))

    alias_to_reference_id: dict[str, str] = {}
    for entry in entries:
        for alias in entry.aliases:
            normalized_alias = normalize_reference_text(alias)
            if not normalized_alias or alias_counts.get(normalized_alias) != 1:
                continue
            alias_to_reference_id[normalized_alias] = entry.reference_id

    prompt_lines = []
    for entry in entries:
        alias_preview = [alias for alias in entry.aliases if alias not in {entry.reference_id, entry.title}]
        if alias_preview:
            prompt_lines.append(f"{entry.reference_id} | {entry.title} | aliases: {', '.join(alias_preview[:2])}")
        else:
            prompt_lines.append(f"{entry.reference_id} | {entry.title}")

    return ReferenceCatalog(
        dataset=dataset,
        entries=entries,
        prompt_text="\n".join(prompt_lines),
        _entries_by_id=entries_by_id,
        _alias_to_reference_id=alias_to_reference_id,
        _normalized_aliases_by_reference_id=normalized_aliases_by_reference_id,
    )


def _extract_law_title(source_text: str) -> str | None:
    cleaned = _clean_reference_title(source_text)
    if not _looks_like_law_entry(cleaned):
        return None

    quoted_match = re.match(
        r'^"(?P<title>.+?)"ги\s+Ўзбекистон Республикаси(?:нинг)?\s+Қонуни.*$',
        cleaned,
    )
    if quoted_match:
        title = quoted_match.group("title").strip()
    else:
        title = cleaned
        title = re.sub(
            r"\s+Ўзбекистон Республикаси(?:нинг)?\s+Қонуни.*$",
            "",
            title,
        ).strip()
        title = re.sub(
            r"\s+Ўзбекистон Республикаси\s+Конституциявий Қонуни.*$",
            "",
            title,
        ).strip()

    if "кодекси" in title.casefold():
        title = re.sub(r"^(.*?кодекси).*$", r"\1", title, flags=re.IGNORECASE).strip()
    elif "тўғрисида" in title.casefold():
        title = re.sub(r"^(.*?тўғрисида).*$", r"\1", title, flags=re.IGNORECASE).strip()

    title = re.sub(r"\s+\(янги таҳрир\)$", "", title, flags=re.IGNORECASE)
    title = title.strip(" .,-")
    title = _strip_wrapping_quotes(title)
    title = re.sub(r"\s+", " ", title).strip(" .,-")
    return title or None


def _looks_like_law_entry(value: str) -> bool:
    normalized = normalize_text(value)
    if "тўғрисида" in normalized or "тўловга қобилиятсизлик" in normalized:
        return True
    if "кодекси" in normalized:
        return True
    if "конституцияси" in normalized:
        return True
    return False


def _build_law_reference_id(title: str, source_text: str) -> str:
    for pattern in (
        r"№\s*([A-ZА-ЯЎҚҒҲ0-9]+(?:-[A-ZА-ЯЎҚҒҲ0-9]+)*)",
        r"([A-ZА-ЯЎҚҒҲ0-9]+(?:-[A-ZА-ЯЎҚҒҲ0-9]+)*)-сон\b",
    ):
        number_match = re.search(pattern, source_text)
        if number_match and any(character.isdigit() for character in number_match.group(1)):
            code = _slugify_reference_fragment(number_match.group(1))
            return f"LAW_{code}"

    core_title = title
    core_title = re.sub(r"^Ўзбекистон Республикасининг\s+", "", core_title)
    core_title = re.sub(r"^Ўзбекистон Республикаси\s+", "", core_title)
    core_title = re.sub(r"^Халқ депутатлари\s+", "", core_title)
    return f"LAW_{_slugify_reference_fragment(core_title)}"


def _build_aliases(title: str, extra_aliases: list[str]) -> tuple[str, ...]:
    values: list[str] = [title, *extra_aliases]
    aliases: list[str] = []
    seen: set[str] = set()

    for value in values:
        for candidate in (value, _latinize_text(value)):
            cleaned = _clean_reference_title(candidate)
            if not cleaned:
                continue
            normalized = normalize_reference_text(cleaned)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            aliases.append(cleaned)

    return tuple(aliases)


def _build_law_alias_candidates(title: str) -> list[str]:
    aliases: list[str] = []
    base_title = _strip_wrapping_quotes(title)
    aliases.append(base_title)

    no_prefix = re.sub(r"^Ўзбекистон Республикасининг\s+", "", base_title)
    no_prefix = re.sub(r"^Ўзбекистон Республикаси\s+", "", no_prefix)
    if no_prefix != base_title:
        aliases.append(no_prefix)

    genitive_tail = re.sub(r"^.+?нинг\s+", "", no_prefix)
    if genitive_tail != no_prefix:
        aliases.append(genitive_tail)
        aliases.append(re.sub(r"лари\s+тўғрисида$", "лар тўғрисида", genitive_tail))
        aliases.append(re.sub(r"си\s+тўғрисида$", " тўғрисида", genitive_tail))

    aliases.append(re.sub(r"лари\s+тўғрисида$", "лар тўғрисида", no_prefix))
    aliases.append(re.sub(r"\s+", " ", no_prefix).strip())
    return [alias for alias in aliases if alias.strip()]


def _clean_reference_title(value: str) -> str:
    cleaned = value.translate(QUOTE_TRANSLATION)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"([(\[])\s+", r"\1", cleaned)
    cleaned = re.sub(r"\s+([)\]])", r"\1", cleaned)
    return cleaned.strip()


def _strip_wrapping_quotes(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith('"') and stripped.endswith('"') and len(stripped) >= 2:
        return stripped[1:-1].strip()
    return stripped


def _slugify_reference_fragment(value: str) -> str:
    transliterated = value.translate(QUOTE_TRANSLATION).upper()
    transliterated = "".join(CYRILLIC_TO_LATIN.get(character, character) for character in transliterated)
    transliterated = re.sub(r"[^A-Z0-9]+", "_", transliterated)
    transliterated = re.sub(r"_+", "_", transliterated).strip("_")
    return transliterated


def _latinize_text(value: str) -> str:
    cleaned = value.translate(QUOTE_TRANSLATION)
    return "".join(
        CYRILLIC_TO_LATIN_TEXT.get(character.upper(), character).lower()
        if character.islower()
        else CYRILLIC_TO_LATIN_TEXT.get(character, character)
        for character in cleaned
    )
