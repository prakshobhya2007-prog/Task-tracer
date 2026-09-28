"""
Domain definitions for Evidence-Grounded Insights.
Enforces the mandatory 5-part insight breakdown:
1. OBSERVATION
2. INFERENCE
3. CONFIDENCE
4. EVIDENCE
5. UNKNOWN / INSUFFICIENT EVIDENCE
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class InsightEnvelope:
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    observation: str = ""
    inference: str = ""
    confidence_score: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNCERTAIN
    evidence: List[str] = field(default_factory=list)  # event_ids, episode_ids, action references
    unknown_disclaimer: str = "Insufficient telemetry to determine internal intent or root cause."
    detector: str = "deterministic_rules"
    model_version: str = "v1.0"
    episode_ids: List[str] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "timestamp": self.timestamp,
            "observation": self.observation,
            "inference": self.inference,
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level.value,
            "evidence": self.evidence,
            "unknown_disclaimer": self.unknown_disclaimer,
            "detector": self.detector,
            "model_version": self.model_version,
            "episode_ids": self.episode_ids,
            "event_ids": self.event_ids,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InsightEnvelope":
        return cls(
            insight_id=data.get("insight_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            observation=data.get("observation", ""),
            inference=data.get("inference", ""),
            confidence_score=float(data.get("confidence_score", 0.0)),
            confidence_level=ConfidenceLevel(data.get("confidence_level", ConfidenceLevel.UNCERTAIN.value)),
            evidence=list(data.get("evidence", [])),
            unknown_disclaimer=data.get("unknown_disclaimer", "Insufficient evidence."),
            detector=data.get("detector", "deterministic_rules"),
            model_version=data.get("model_version", "v1.0"),
            episode_ids=list(data.get("episode_ids", [])),
            event_ids=list(data.get("event_ids", [])),
            metadata=dict(data.get("metadata", {})),
        )
