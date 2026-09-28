"""
Episode Envelope domain definition.
Represents a sessionized unit of user computer activity.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class EpisodeEnvelope:
    episode_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = None
    start_monotonic: float = 0.0
    end_monotonic: Optional[float] = None
    applications: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    processes: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    action_sequence: List[str] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    switch_count: int = 0
    event_ids: List[str] = field(default_factory=list)
    candidate_task: Optional[str] = None
    confidence: float = 1.0
    workspace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "start_monotonic": self.start_monotonic,
            "end_monotonic": self.end_monotonic,
            "applications": self.applications,
            "files": self.files,
            "processes": self.processes,
            "domains": self.domains,
            "action_sequence": self.action_sequence,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "switch_count": self.switch_count,
            "event_ids": self.event_ids,
            "candidate_task": self.candidate_task,
            "confidence": self.confidence,
            "workspace": self.workspace,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EpisodeEnvelope":
        return cls(
            episode_id=data.get("episode_id", str(uuid.uuid4())),
            start_time=data.get("start_time", datetime.now(timezone.utc).isoformat()),
            end_time=data.get("end_time"),
            start_monotonic=float(data.get("start_monotonic", 0.0)),
            end_monotonic=data.get("end_monotonic"),
            applications=list(data.get("applications", [])),
            files=list(data.get("files", [])),
            processes=list(data.get("processes", [])),
            domains=list(data.get("domains", [])),
            action_sequence=list(data.get("action_sequence", [])),
            success_count=int(data.get("success_count", 0)),
            failure_count=int(data.get("failure_count", 0)),
            switch_count=int(data.get("switch_count", 0)),
            event_ids=list(data.get("event_ids", [])),
            candidate_task=data.get("candidate_task"),
            confidence=float(data.get("confidence", 1.0)),
            workspace=data.get("workspace"),
            metadata=dict(data.get("metadata", {})),
        )
