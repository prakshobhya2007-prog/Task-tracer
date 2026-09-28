# Security Policy & Protections

## Core Security Rules

1. **Read-Only Intelligence Core**: The AI engine has **zero** shell execution, zero filesystem modification capabilities, and zero external command execution permissions.
2. **Prompt Injection Defense**: All telemetry strings pass through `PromptGuard.sanitize_untrusted_string()` to scrub malicious system overrides before being serialized into JSON blocks.
3. **Secret Redaction**: Passwords, bearer tokens, JWTs, API keys, Slack tokens, and GitHub personal access tokens are scrubbed using regular expression redactors before storage.
4. **Local API Binding**: The FastAPI server binds to `127.0.0.1` locally by default.
