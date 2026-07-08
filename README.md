# Telegram Monitoring Automation System

This project implements a small batch ETL flow for weekly Telegram monitoring reports.

Pipeline:

1. Calculate the report period.
2. Fetch posts from Telegram public channels.
3. Ignore media posts without caption or text.
4. Classify posts in Gemini batch requests.
5. Run deterministic regression checks on every classification result.
6. Audit every classified post in Gemini batch requests.
7. Aggregate audited category statistics by council.
8. Generate Uzbek narrative sections from deterministic aggregation facts.
9. Validate narrative language, numbers, and trend constraints deterministically.
10. Produce a DOCX report by updating the reference document layout in place.

## Requirements

- Python 3.13+
- Telegram API credentials in environment variables
- One or more Gemini API keys in `config.yaml`

Environment variables:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `GEMINI_API_KEY_1`
- `GEMINI_API_KEY_2`
- `GEMINI_API_KEY_3`

## Install

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Generated artifacts are written under `data/`:

- `data/raw_posts/raw_posts.json`
- `data/classified_posts/classified_posts.json`
- `data/regression_checks/classification_regression_checks.json`
- `data/audited_posts/audited_posts.json`
- `data/regression_checks/audit_regression_checks.json`
- `data/aggregated_stats/aggregated_stats.json`
- `data/narrative/narrative.json`
- `data/narrative/narrative_validation.json`
- `data/reports/*.docx`

## Configuration

Main settings live in [config.yaml](/D:/ozod/coding/python/telegram-automation-system/tg-automation-system/config.yaml).

Gemini key rotation is configured as an ordered list:

```yaml
gemini:
  api_keys:
    - GEMINI_API_KEY_1
    - GEMINI_API_KEY_2
    - GEMINI_API_KEY_3
  model: gemini-3.5-flash
```

The pipeline always starts with the first key. If Gemini returns a daily quota exhaustion error for the active key, the failed request is retried automatically with the next configured key. Temporary 429 rate limits and 5xx errors stay on the same key and use retry with backoff.

Classification uses `references/classification_specification_v2.md` as the only authoritative taxonomy source. The `24_ta_masala.md` and `Qonunlar_taqsimoti.md` files remain active only as reference datasets for validation and audit support.

Narrative generation uses `references/narrative_specification_v1.md` as the authoritative narrative rules source. The generator receives only deterministic aggregation facts, and `src/narrative_validator.py` blocks prohibited language, unsupported trend language, and numeric drift before DOCX generation.

The implementation uses the provided reference report as the visual template source so the output stays as close as possible to the original DOCX structure, table layout, and heading pattern.
