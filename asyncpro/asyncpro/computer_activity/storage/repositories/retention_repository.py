"""
Data Retention Lifecycle and Privacy Operations Repository.
Implements purge policies, clear today, delete all data, and export data.
"""
from datetime import datetime, timedelta, timezone
import json
from typing import Any, Dict
from computer_activity.storage.sqlite.database import Database


class RetentionRepository:
    def __init__(self, db: Database):
        self.db = db

    def enforce_retention_policy(
        self,
        raw_retention_days: int = 1,
        episode_retention_days: int = 30,
        insight_retention_days: int = 90,
    ) -> Dict[str, int]:
        """Purges telemetry data exceeding configured retention thresholds."""
        now = datetime.now(timezone.utc)
        
        raw_cutoff = (now - timedelta(days=raw_retention_days)).isoformat()
        ep_cutoff = (now - timedelta(days=episode_retention_days)).isoformat()
        ins_cutoff = (now - timedelta(days=insight_retention_days)).isoformat()

        events_deleted = self.db.execute_write("DELETE FROM events WHERE timestamp < ?;", (raw_cutoff,))
        episodes_deleted = self.db.execute_write("DELETE FROM episodes WHERE start_time < ?;", (ep_cutoff,))
        insights_deleted = self.db.execute_write("DELETE FROM insights WHERE timestamp < ?;", (ins_cutoff,))

        return {
            "events_purged": events_deleted,
            "episodes_purged": episodes_deleted,
            "insights_purged": insights_deleted,
        }

    def clear_today(self) -> Dict[str, int]:
        """Clears all activity data logged today (UTC)."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        e_cnt = self.db.execute_write("DELETE FROM events WHERE timestamp >= ?;", (today_start,))
        ep_cnt = self.db.execute_write("DELETE FROM episodes WHERE start_time >= ?;", (today_start,))
        i_cnt = self.db.execute_write("DELETE FROM insights WHERE timestamp >= ?;", (today_start,))

        return {
            "events_deleted": e_cnt,
            "episodes_deleted": ep_cnt,
            "insights_deleted": i_cnt,
        }

    def delete_all_data(self) -> Dict[str, int]:
        """Completely wipes all user activity storage tables."""
        tables = ["events", "sessions", "episodes", "features", "patterns", "anomalies", "entities", "relationships", "embeddings", "insights"]
        total_deleted = 0
        counts = {}
        for tbl in tables:
            cnt = self.db.execute_write(f"DELETE FROM {tbl};")
            counts[tbl] = cnt
            total_deleted += cnt
        return counts

    def export_all_data() -> Dict[str, Any]:
        """Exports all stored telemetry, episodes, and insights into a privacy-safe JSON dump."""
        events = [dict(r) for r in self.db.execute_read("SELECT * FROM events;")]
        episodes = [dict(r) for r in self.db.execute_read("SELECT * FROM episodes;")]
        insights = [dict(r) for r in self.db.execute_read("SELECT * FROM insights;")]
        patterns = [dict(r) for r in self.db.execute_read("SELECT * FROM patterns;")]

        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "events_count": len(events),
            "episodes_count": len(episodes),
            "insights_count": len(insights),
            "events": events,
            "episodes": episodes,
            "insights": insights,
            "patterns": patterns,
        }
