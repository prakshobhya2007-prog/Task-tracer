"""
Event Repository for storing and retrieving Canonical Events in SQLite.
"""
import json
from typing import List, Optional
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.storage.sqlite.database import Database


class EventRepository:
    def __init__(self, db: Database):
        self.db = db

    def save_event(self, event: CanonicalEvent):
        sql = """
        INSERT OR REPLACE INTO events (
            event_id, timestamp, monotonic_timestamp, platform, collector,
            event_type, process_json, application, resource, metadata_json,
            privacy_class, redaction_status, schema_version, priority
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        proc_json = json.dumps(event.process.to_dict()) if event.process else None
        meta_json = json.dumps(event.metadata) if event.metadata else "{}"
        self.db.execute_write(sql, (
            event.event_id,
            event.timestamp,
            event.monotonic_timestamp,
            event.platform,
            event.collector,
            event.event_type,
            proc_json,
            event.application,
            event.resource,
            meta_json,
            event.privacy_class.value,
            event.redaction_status.value,
            event.schema_version,
            event.priority.value,
        ))

    def save_batch(self, events: List[CanonicalEvent]):
        if not events:
            return
        sql = """
        INSERT OR REPLACE INTO events (
            event_id, timestamp, monotonic_timestamp, platform, collector,
            event_type, process_json, application, resource, metadata_json,
            privacy_class, redaction_status, schema_version, priority
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params_list = []
        for e in events:
            proc_json = json.dumps(e.process.to_dict()) if e.process else None
            meta_json = json.dumps(e.metadata) if e.metadata else "{}"
            params_list.append((
                e.event_id, e.timestamp, e.monotonic_timestamp, e.platform, e.collector,
                e.event_type, proc_json, e.application, e.resource, meta_json,
                e.privacy_class.value, e.redaction_status.value, e.schema_version, e.priority.value
            ))
        self.db.execute_write_batch(sql, params_list)

    def get_recent_events(self, limit: int = 100) -> List[CanonicalEvent]:
        sql = "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?;"
        rows = self.db.execute_read(sql, (limit,))
        events = []
        for row in rows:
            d = dict(row)
            if d.get("process_json"):
                d["process"] = json.loads(d["process_json"])
            if d.get("metadata_json"):
                d["metadata"] = json.loads(d["metadata_json"])
            events.append(CanonicalEvent.from_dict(d))
        return events

    def get_events_in_range(self, start_time: str, end_time: str) -> List[CanonicalEvent]:
        sql = "SELECT * FROM events WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp ASC;"
        rows = self.db.execute_read(sql, (start_time, end_time))
        events = []
        for row in rows:
            d = dict(row)
            if d.get("process_json"):
                d["process"] = json.loads(d["process_json"])
            if d.get("metadata_json"):
                d["metadata"] = json.loads(d["metadata_json"])
            events.append(CanonicalEvent.from_dict(d))
        return events
