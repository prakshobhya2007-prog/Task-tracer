# System Architecture Documentation

The **AI Computer Activity Intelligence Platform** processes system telemetry through a strictly decoupled, layered architecture:

```text
Computer OS (Linux / Windows / macOS)
   ↓
Platform Collectors (psutil / proc / Win32 / hooks)
   ↓
Canonical Event Normalization
   ↓
Privacy Firewall (Classification, Redaction, Exclusions, Dropping)
   ↓
Event Ingestion Queue (Backpressure, Coalescing, Priority Routing)
   ↓
SQLite Local Database (WAL Mode, Single Writer Queue)
   ↓
Deterministic Sessionization (Episode Reconstruction)
   ↓
Deterministic Feature Extraction (Metrics & Sequence Entropy)
   ↓
Statistical & ML Pattern Analysis (Sequence Mining & Anomaly Engine)
   ↓
Behaviour Graph & Semantic Vector Embeddings
   ↓
Hybrid Retrieval Engine (SQL + Graph + Vector)
   ↓
Prompt Guard & Constrained LLM Interpreter
   ↓
Evidence-Grounded Insight Ledger
   ↓
FastAPI Server & Web Dashboard UI
```

## Modular Structure

1. **`core/domain`**: Canonical Event Envelopes, Episode Envelopes, Entities, and 5-part Insight Envelopes.
2. **`core/privacy` & `security/redaction`**: Privacy classification engine and secret scrubbing.
3. **`core/ingestion`**: Priority queue with coalescing and backpressure handling.
4. **`storage`**: SQLite connection manager with WAL mode, schema migrations, and repositories.
5. **`core/sessionization`**: Explainable activity gap boundary detector.
6. **`core/patterns` & `core/anomaly`**: Sequence miner and multi-level anomaly detection.
7. **`core/graph` & `core/retrieval`**: Behaviour graph traversal and hybrid retrieval.
8. **`core/inference` & `security/prompt_guard`**: Prompt guard security and schema-constrained AI interpretation.
9. **`api` & `ui`**: FastAPI REST endpoints and interactive web dashboard.
