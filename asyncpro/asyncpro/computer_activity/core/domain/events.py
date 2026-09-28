"""
Canonical Event Model definition.
Defines versioned canonical event envelope, process identity, privacy classifications,
and redaction statuses.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import time
from typing import Any, Dict, Optional
import uuid


class PrivacyClass(str, Enum):
    PUBLIC_METADATA = "PUBLIC_METADATA"
    PERSONAL_METADATA = "PERSONAL_METADATA"
    SENSITIVE_METADATA = "SENSITIVE_METADATA"
    SECRET = "SECRET"
    FORBIDDEN = "FORBIDDEN"


class RedactionStatus(str, Enum):
    NONE = "none"
    REDACTED = "redacted"
    HASHED = "hashed"
    DISCARDED = "discarded"


class EventPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ProcessIdentity:
    pid: int
    start_time: str
    executable: str
    name: str
    instance_id: str = field(init=False)

    def __post_init__(self):
        raw_key = f"{self.executable}:{self.pid}:{self.start_time}"
        self.instance_id = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "start_time": self.start_time,
            "executable": self.executable,
            "name": self.name,
            "instance_id": self.instance_id,
        }


@dataclass
class CanonicalEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    monotonic_timestamp: float = field(default_factory=time.monotonic)
    platform: str = "linux"
    collector: str = "generic"
    event_type: str = "activity.generic"
    process: Optional[ProcessIdentity] = None
    application: str = "unknown"
    resource: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    privacy_class: PrivacyClass = PrivacyClass.PUBLIC_METADATA
    redaction_status: RedactionStatus = RedactionStatus.NONE
    schema_version: int = 1
    priority: EventPriority = EventPriority.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "monotonic_timestamp": self.monotonic_timestamp,
            "platform": self.platform,
            "collector": self.collector,
            "event_type": self.event_type,
            "process": self.process.to_dict() if self.process else None,
            "application": self.application,
            "resource": self.resource,
            "metadata": self.metadata,
            "privacy_class": self.privacy_class.value,
            "redaction_status": self.redaction_status.value,
            "schema_version": self.schema_version,
            "priority": self.priority.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalEvent":
        proc_data = data.get("process")
        proc = None
        if proc_data:
            proc = ProcessIdentity(
                pid=proc_data.get("pid", 0),
                start_time=str(proc_data.get("start_time", "")),
                executable=str(proc_data.get("executable", "")),
                name=str(proc_data.get("name", "")),
            )
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            monotonic_timestamp=float(data.get("monotonic_timestamp", time.monotonic())),
            platform=data.get("platform", "linux"),
            collector=data.get("collector", "generic"),
            event_type=data.get("event_type", "activity.generic"),
            process=proc,
            application=data.get("application", "unknown"),
            resource=data.get("resource"),
            metadata=data.get("metadata", {}),
            privacy_class=PrivacyClass(data.get("privacy_class", PrivacyClass.PUBLIC_METADATA.value)),
            redaction_status=RedactionStatus(data.get("redaction_status", RedactionStatus.NONE.value)),
            schema_version=int(data.get("schema_version", 1)),
            priority=EventPriority(data.get("priority", EventPriority.MEDIUM.value)),
        )
