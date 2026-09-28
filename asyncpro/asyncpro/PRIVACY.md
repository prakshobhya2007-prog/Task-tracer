# Privacy Architecture & Data Governance

## Default Exclusion Criteria

The platform **never** collects:
- Keystrokes or input logging
- Password input fields
- Authentication tokens
- Clipboard contents
- Screenshots or screen capture data
- Microphone audio
- Camera video
- Raw browser HTML page contents
- Full browser URLs containing query params or tokens

## Privacy Classifications

- `PUBLIC_METADATA`: Process name, application name, process lifecycle, CPU/RAM usage.
- `PERSONAL_METADATA`: Registrable browser domain name, sanitized project file path.
- `SENSITIVE_METADATA`: Terminal command strings (sanitized).
- `SECRET`: Passwords, tokens, API keys (Redacted/Dropped).
- `FORBIDDEN`: Keystrokes, raw screen content (Dropped immediately).

## Data Deletion & Export

User controls:
- **Pause Collection**: Stops telemetry recording instantly.
- **Clear Today**: Deletes all entries recorded today.
- **Delete All Data**: Completely purges database tables.
- **Export Safe Data**: Exports a JSON dump of stored events and insights.
