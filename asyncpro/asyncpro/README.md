# AI Computer Activity Intelligence Platform

A production-grade, local-first, privacy-first computer activity intelligence system.
The system observes low-level computer telemetry, sessionizes raw events into explainable activity episodes, detects repeated workflows/anomalies/context switching, constructs a behaviour graph, and interprets findings using evidence-grounded AI interpretation.

---

## Key Features

- **Privacy Firewall**: Filters and redacts secrets, tokens, API keys, passwords, private paths, and URLs before storage or AI exposure. Keystrokes, clipboard, screenshots, camera, and raw browser content are **never** collected.
- **Canonical Event Model**: Standardized, versioned event envelopes with wall-clock and monotonic timestamps, process instance hashes, and privacy classifications.
- **Explainable Sessionization**: Deterministic episode boundary engine based on gap thresholds and focus transitions.
- **Multi-Level Anomaly Detection**: Rule-based thresholds, statistical Z-score/MAD, and ML Isolation Forest scoring.
- **Behaviour Graph & Sequence Mining**: Graph modeling of applications, episodes, files, processes, domains, and failure nodes for rich trajectory analysis.
- **Constrained AI Interpretation**: Generates structured 5-part insights (`OBSERVATION`, `INFERENCE`, `CONFIDENCE`, `EVIDENCE`, `UNKNOWN / INSUFFICIENT EVIDENCE`).
- **Prompt Injection Defense**: Sanitizes untrusted telemetry strings and enforces JSON structure to prevent LLM instruction hijacking.
- **Web Dashboard & REST API**: Modern dark-mode interface with live status monitoring, timeline visualization, natural-language query search, pause controls, and data deletion tools.

---

## Getting Started

### Prerequisites
- Python 3.11+
- SQLite3

### Installation

1. Create a virtual environment and install dependencies:
   ```bash
   uv venv .venv --python 3.11
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   uv pip install -r requirements.txt
   ```

2. Run database migrations:
   ```bash
   python -m computer_activity.apps.cli.main migrate
   ```

3. Start the API Server & Dashboard:
   ```bash
   python -m computer_activity.apps.cli.main serve
   ```
   Open your browser to `http://127.0.0.1:8000` to access the interactive web interface.

---

## Replaying Demonstration Scenarios

To test the end-to-end intelligence engine offline:

```bash
python -m computer_activity.apps.cli.main replay --scenario cpp_debugging_loop
```

Or click **"Replay C++ Debugging Loop"** directly inside the Web Dashboard!

---

## Running Tests

Execute the full pytest suite:

```bash
pytest computer_activity/tests
```

---

## Governance & Controls

- **Pause Collection**: Toggle monitoring on/off instantly via the dashboard header button or `POST /api/collection/pause`.
- **Clear Today's Data**: `POST /api/data/delete?scope=today`
- **Delete All Data**: `POST /api/data/delete?scope=all`
- **Export Safe JSON**: `GET /api/data/export`
