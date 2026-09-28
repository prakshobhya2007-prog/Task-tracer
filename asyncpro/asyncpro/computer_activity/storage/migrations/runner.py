"""
Database Migration Runner.
Applies DDL schema migrations for all required tables and indexes.
"""
import logging
from computer_activity.storage.sqlite.database import Database

logger = logging.getLogger(__name__)

MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL
    );
    """,
    """
    -- Migration 1: Initial Core Schema
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        monotonic_timestamp REAL NOT NULL,
        platform TEXT NOT NULL,
        collector TEXT NOT NULL,
        event_type TEXT NOT NULL,
        process_json TEXT,
        application TEXT NOT NULL,
        resource TEXT,
        metadata_json TEXT,
        privacy_class TEXT NOT NULL,
        redaction_status TEXT NOT NULL,
        schema_version INTEGER NOT NULL DEFAULT 1,
        priority TEXT NOT NULL DEFAULT 'MEDIUM'
    );

    CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_events_collector ON events(collector);
    CREATE INDEX IF NOT EXISTS idx_events_app ON events(application);

    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        start_time TEXT NOT NULL,
        end_time TEXT,
        event_count INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS episodes (
        episode_id TEXT PRIMARY KEY,
        start_time TEXT NOT NULL,
        end_time TEXT,
        start_monotonic REAL NOT NULL,
        end_monotonic REAL,
        applications_json TEXT,
        files_json TEXT,
        processes_json TEXT,
        domains_json TEXT,
        action_sequence_json TEXT,
        success_count INTEGER DEFAULT 0,
        failure_count INTEGER DEFAULT 0,
        switch_count INTEGER DEFAULT 0,
        event_ids_json TEXT,
        candidate_task TEXT,
        confidence REAL DEFAULT 1.0,
        workspace TEXT,
        metadata_json TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_episodes_start ON episodes(start_time);

    CREATE TABLE IF NOT EXISTS features (
        feature_id TEXT PRIMARY KEY,
        episode_id TEXT NOT NULL,
        feature_name TEXT NOT NULL,
        feature_value REAL NOT NULL,
        FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS patterns (
        pattern_id TEXT PRIMARY KEY,
        sequence_json TEXT NOT NULL,
        frequency INTEGER DEFAULT 1,
        label TEXT,
        confidence REAL DEFAULT 1.0,
        first_seen TEXT,
        last_seen TEXT
    );

    CREATE TABLE IF NOT EXISTS anomalies (
        anomaly_id TEXT PRIMARY KEY,
        episode_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        score REAL NOT NULL,
        rule_reasons_json TEXT,
        detector TEXT NOT NULL,
        FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        name TEXT NOT NULL,
        metadata_json TEXT
    );

    CREATE TABLE IF NOT EXISTS relationships (
        rel_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        rel_type TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        metadata_json TEXT
    );

    CREATE TABLE IF NOT EXISTS embeddings (
        embedding_id TEXT PRIMARY KEY,
        episode_id TEXT NOT NULL,
        vector_json TEXT NOT NULL,
        model_name TEXT NOT NULL,
        FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS insights (
        insight_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        observation TEXT NOT NULL,
        inference TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        confidence_level TEXT NOT NULL,
        evidence_json TEXT NOT NULL,
        unknown_disclaimer TEXT NOT NULL,
        detector TEXT NOT NULL,
        model_version TEXT NOT NULL,
        episode_ids_json TEXT,
        event_ids_json TEXT,
        metadata_json TEXT
    );

    CREATE TABLE IF NOT EXISTS model_runs (
        run_id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        prompt_version TEXT NOT NULL,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        latency_ms REAL DEFAULT 0.0,
        timestamp TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS privacy_rules (
        rule_id TEXT PRIMARY KEY,
        rule_type TEXT NOT NULL,
        pattern TEXT NOT NULL,
        action TEXT NOT NULL,
        enabled INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value_json TEXT NOT NULL
    );
    """
]


class MigrationRunner:
    """Executes database DDL migrations idempotently."""

    def __init__(self, db: Database):
        self.db = db

    def run_migrations(self):
        # Apply base schema_migrations table first
        self.db.execute_write(MIGRATIONS[0])

        rows = self.db.execute_read("SELECT version FROM schema_migrations;")
        applied_versions = {row["version"] for row in rows}

        for version, sql_script in enumerate(MIGRATIONS[1:], start=1):
            if version not in applied_versions:
                logger.info(f"Applying database migration version {version}...")
                statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
                for stmt in statements:
                    self.db.execute_write(stmt)
                self.db.execute_write(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, datetime('now'));",
                    (version,),
                )
                logger.info(f"Migration version {version} applied successfully.")
