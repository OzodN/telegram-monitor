# Error Matrix

| Error Type | Action |
|---|---|
| Daily Gemini quota exhaustion for active key | Rotate to next key and retry operation |
| All Gemini keys exhausted for daily quota | Stop run with terminal exhaustion error |
| Gemini `429` not identified as daily quota exhaustion | Retry same key with backoff |
| Gemini `500` | Retry same key with backoff |
| Gemini `502` | Retry same key with backoff |
| Gemini `503` | Retry same key with backoff |
| Gemini `504` | Retry same key with backoff |
| Gemini timeout | Retry same key with backoff |
| Retryable transport/network read/write/connect error | Retry same key with backoff |
| Invalid structured JSON / response-format failure | Retry same key |
| Missing classification decision for a post in a batch | Mark classification batch failed |
| All classification batches failed | Stop run with runtime error |
| Invalid regression-check result | Stop run with validation error |
| Aggregation identity mismatch | Stop run with validation error |
| Narrative validation failure | Stop run with validation error (Note: prefix formatting anomalies are auto-healed in-place, while value/prohibited-word mismatches trigger a run failure) |
| Single Telegram channel fetch failure | Log channel failure and continue other channels |
| Subscriber-count fetch failure | Log warning and continue with `null` subscriber count |

