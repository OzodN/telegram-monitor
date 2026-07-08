# API Rotation

- **Key storage model**
  - Gemini API keys are configured as an ordered list in `config.yaml` under `gemini.api_keys`.
  - Each list item may be a direct key value or an environment-variable name resolved at runtime.
  - At least one non-empty Gemini key is required.
  - The Gemini client keeps one active key at a time and caches per-key client instances.

- **Rotation rules**
  - Processing always starts with the first configured key.
  - Key rotation is sequential and forward-only within a run.
  - Rotation occurs only when the active key is detected as daily quota exhausted.
  - When daily quota exhaustion is detected:
    - current request stops using the active key
    - client advances to the next configured key
    - the failed operation is retried with the next key
  - If there is no next key, the run raises all-keys-exhausted failure.

- **Retry rules**
  - Retries on the same key apply to structured-output/response-format failures, timeout/connection failures, temporary non-daily `429` errors, and retryable `5xx` server errors.
  - On every retry for a connection or timeout error, the active connection pool is dropped (`_drop_client`) and a fresh `genai.Client` is instantiated to ensure clean socket recovery.
  - If the configured local retry attempts are exhausted for the active key, the key is rotated sequentially.
  - Immediate key rotation (bypassing local retries) is triggered strictly on daily quota exhaustion or invalid auth keys.
  - A run-wide throttle applies to every request.
  - Retry delay uses the `Retry-After` header or error-embedded retry hints when available, failing back to exponential backoff with jitter.

- **Exhaustion rules**
  - Daily quota exhaustion is distinguished from temporary retryable rate limiting.
  - Daily quota exhaustion is inferred from Gemini API error status/message/details indicating free-tier or per-day quota exhaustion.
  - Only daily quota exhaustion triggers key rotation.
  - Temporary rate limits and transient server/transport errors do not rotate keys.
  - If every configured key is daily-quota exhausted, the client raises `GeminiAllKeysExhaustedError` and the run cannot continue.
