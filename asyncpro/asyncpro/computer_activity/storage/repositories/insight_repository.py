"""
Insight Repository for persisting validated insights and evidence ledgers.
"""
import json
from typing import List, Optional
from computer_activity.core.domain.insights import ConfidenceLevel, InsightEnvelope
from computer_activity.storage.sqlite.database import Database


class InsightRepository:
    def __init__(self, db: Database):
        self.db = db

    def save_insight(self, insight: InsightEnvelope):
        sql = """
        INSERT OR REPLACE INTO insights (
            insight_id, timestamp, observation, inference, confidence_score,
            confidence_level, evidence_json, unknown_disclaimer, detector,
            model_version, episode_ids_json, event_ids_json, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.db.execute_write(sql, (
            insight.insight_id,
            insight.timestamp,
            insight.observation,
            insight.inference,
            insight.confidence_score,
            insight.confidence_level.value,
            json.dumps(insight.evidence),
            insight.unknown_disclaimer,
            insight.detector,
            insight.model_version,
            json.dumps(insight.episode_ids),
            json.dumps(insight.event_ids),
            json.dumps(insight.metadata),
        ))

    def get_recent_insights(self, limit: int = 50) -> List[InsightEnvelope]:
        sql = "SELECT * FROM insights ORDER BY timestamp DESC LIMIT ?;"
        rows = self.db.execute_read(sql, (limit,))
        return [self._row_to_insight(row) for row in rows]

    def get_insight_by_id(self, insight_id: str) -> Optional[InsightEnvelope]:
        sql = "SELECT * FROM insights WHERE insight_id = ?;"
        rows = self.db.execute_read(sql, (insight_id,))
        if rows:
            return self._row_to_insight(rows[0])
        return None

    def _row_to_insight(self, row) -> InsightEnvelope:
        d = dict(row)
        return InsightEnvelope(
            insight_id=d["insight_id"],
            timestamp=d["timestamp"],
            observation=d["observation"],
            inference=d["inference"],
            confidence_score=float(d["confidence_score"]),
            confidence_level=ConfidenceLevel(d["confidence_level"]),
            evidence=json.loads(d["evidence_json"] or "[]"),
            unknown_disclaimer=d["unknown_disclaimer"],
            detector=d["detector"],
            model_version=d["model_version"],
            episode_ids=json.loads(d["episode_ids_json"] or "[]"),
            event_ids=json.loads(d["event_ids_json"] or "[]"),
            metadata=json.loads(d["metadata_json"] or "{}"),
        )
