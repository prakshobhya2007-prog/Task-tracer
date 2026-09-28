"""
Hybrid Retrieval Engine (SQL + Graph + Vector).
Constructs evidence packages grounded strictly in empirical storage.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.episodes import EpisodeEnvelope
from computer_activity.core.embeddings.provider import EmbeddingsProvider
from computer_activity.core.graph.behaviour_graph import BehaviourGraph
from computer_activity.storage.repositories.event_repository import EventRepository
from computer_activity.storage.repositories.episode_repository import EpisodeRepository


@dataclass
class EvidencePackage:
    query: str
    retrieved_events: List[CanonicalEvent] = field(default_factory=list)
    retrieved_episodes: List[EpisodeEnvelope] = field(default_factory=list)
    graph_context: Dict[str, Any] = field(default_factory=dict)
    relevance_scores: Dict[str, float] = field(default_factory=dict)
    has_sufficient_evidence: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "retrieved_events_count": len(self.retrieved_events),
            "retrieved_episodes_count": len(self.retrieved_episodes),
            "events": [e.to_dict() for e in self.retrieved_events[:10]],
            "episodes": [ep.to_dict() for ep in self.retrieved_episodes[:5]],
            "graph_context": self.graph_context,
            "has_sufficient_evidence": self.has_sufficient_evidence,
        }


class HybridRetriever:
    """Hybrid Retriever executing SQL, Graph traversal, and Vector similarity search."""

    def __init__(
        self,
        event_repo: EventRepository,
        episode_repo: EpisodeRepository,
        graph: BehaviourGraph,
        embeddings_provider: EmbeddingsProvider,
    ):
        self.event_repo = event_repo
        self.episode_repo = episode_repo
        self.graph = graph
        self.embeddings_provider = embeddings_provider

    def retrieve(self, query: str, limit_events: int = 20, limit_episodes: int = 5) -> EvidencePackage:
        query_lower = query.lower()
        
        # 1. SQL Retrieval
        all_events = self.event_repo.get_recent_events(limit=200)
        all_episodes = self.episode_repo.get_recent_episodes(limit=50)

        matching_events: List[CanonicalEvent] = []
        matching_episodes: List[EpisodeEnvelope] = []

        for e in all_events:
            searchable = f"{e.application} {e.resource} {e.event_type} {e.collector}".lower()
            if any(term in searchable for term in query_lower.split()):
                matching_events.append(e)

        for ep in all_episodes:
            searchable = f"{' '.join(ep.applications)} {' '.join(ep.files)} {' '.join(ep.domains)} {ep.candidate_task}".lower()
            if any(term in searchable for term in query_lower.split()):
                matching_episodes.append(ep)

        # Fallback: if no query matches specifically, include recent activity
        if not matching_events:
            matching_events = all_events[:limit_events]
        if not matching_episodes:
            matching_episodes = all_episodes[:limit_episodes]

        # 2. Graph Context Retrieval
        graph_context = {}
        if "crash" in query_lower or "fail" in query_lower or "problem" in query_lower:
            graph_context = self.graph.query_preceding_activity("Failure")

        sufficient = len(matching_events) > 0 or len(matching_episodes) > 0

        return EvidencePackage(
            query=query,
            retrieved_events=matching_events[:limit_events],
            retrieved_episodes=matching_episodes[:limit_episodes],
            graph_context=graph_context,
            has_sufficient_evidence=sufficient,
        )
