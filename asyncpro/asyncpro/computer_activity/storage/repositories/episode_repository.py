"""
Episode Repository for persisting activity episodes in SQLite.
"""
import json
from typing import List, Optional
from computer_activity.core.domain.episodes import EpisodeEnvelope
from computer_activity.storage.sqlite.database import Database


class EpisodeRepository:
    def __init__(self, db: Database):
        self.db = db

    def save_episode(self, episode: EpisodeEnvelope):
        sql = """
        INSERT OR REPLACE INTO episodes (
            episode_id, start_time, end_time, start_monotonic, end_monotonic,
            applications_json, files_json, processes_json, domains_json,
            action_sequence_json, success_count, failure_count, switch_count,
            event_ids_json, candidate_task, confidence, workspace, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.db.execute_write(sql, (
            episode.episode_id,
            episode.start_time,
            episode.end_time,
            episode.start_monotonic,
            episode.end_monotonic,
            json.dumps(episode.applications),
            json.dumps(episode.files),
            json.dumps(episode.processes),
            json.dumps(episode.domains),
            json.dumps(episode.action_sequence),
            episode.success_count,
            episode.failure_count,
            episode.switch_count,
            json.dumps(episode.event_ids),
            episode.candidate_task,
            episode.confidence,
            episode.workspace,
            json.dumps(episode.metadata),
        ))

    def get_recent_episodes(self, limit: int = 50) -> List[EpisodeEnvelope]:
        sql = "SELECT * FROM episodes ORDER BY start_time DESC LIMIT ?;"
        rows = self.db.execute_read(sql, (limit,))
        return [self._row_to_envelope(row) for row in rows]

    def get_episode_by_id(self, episode_id: str) -> Optional[EpisodeEnvelope]:
        sql = "SELECT * FROM episodes WHERE episode_id = ?;"
        rows = self.db.execute_read(sql, (episode_id,))
        if rows:
            return self._row_to_envelope(rows[0])
        return None

    def _row_to_envelope(self, row) -> EpisodeEnvelope:
        d = dict(row)
        return EpisodeEnvelope(
            episode_id=d["episode_id"],
            start_time=d["start_time"],
            end_time=d["end_time"],
            start_monotonic=float(d["start_monotonic"]),
            end_monotonic=float(d["end_monotonic"]) if d["end_monotonic"] is not None else None,
            applications=json.loads(d["applications_json"] or "[]"),
            files=json.loads(d["files_json"] or "[]"),
            processes=json.loads(d["processes_json"] or "[]"),
            domains=json.loads(d["domains_json"] or "[]"),
            action_sequence=json.loads(d["action_sequence_json"] or "[]"),
            success_count=int(d["success_count"] or 0),
            failure_count=int(d["failure_count"] or 0),
            switch_count=int(d["switch_count"] or 0),
            event_ids=json.loads(d["event_ids_json"] or "[]"),
            candidate_task=d["candidate_task"],
            confidence=float(d["confidence"] or 1.0),
            workspace=d["workspace"],
            metadata=json.loads(d["metadata_json"] or "{}"),
        )
