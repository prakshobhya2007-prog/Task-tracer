"""
First-Class Behaviour Graph Engine.
Constructs directed graph nodes (Application, Episode, File, Process, Domain, Failure)
and relationships for rich graph traversal queries.
"""
from typing import Any, Dict, List, Set, Tuple
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.episodes import EpisodeEnvelope


class BehaviourGraph:
    """In-memory and persistent behaviour graph model."""

    def __init__(self):
        # nodes: node_id -> {type, label, attributes}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # edges: list of (source_id, target_id, rel_type, weight)
        self.edges: List[Tuple[str, str, str, float]] = []

    def add_node(self, node_id: str, node_type: str, label: str, attributes: Dict[str, Any] = None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label": label,
                "attributes": attributes or {},
            }

    def add_edge(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0):
        self.edges.append((source_id, target_id, rel_type, weight))

    def ingest_episode(self, episode: EpisodeEnvelope, events: List[CanonicalEvent]):
        """Builds graph nodes and relationships for an episode."""
        ep_node_id = f"ep:{episode.episode_id}"
        self.add_node(ep_node_id, "Episode", f"Episode {episode.episode_id[:6]}", episode.to_dict())

        # Link Applications
        for app in episode.applications:
            app_id = f"app:{app}"
            self.add_node(app_id, "Application", app)
            self.add_edge(ep_node_id, app_id, "USES_APP", 1.0)

        # Link Files
        for f in episode.files:
            file_id = f"file:{f}"
            self.add_node(file_id, "File", f)
            self.add_edge(ep_node_id, file_id, "MODIFIES_FILE", 1.0)

        # Link Domains
        for d in episode.domains:
            dom_id = f"dom:{d}"
            self.add_node(dom_id, "Domain", d)
            self.add_edge(ep_node_id, dom_id, "SEARCHES_DOMAIN", 1.0)

        # Link Failures
        if episode.failure_count > 0:
            fail_id = f"fail:{episode.episode_id}"
            self.add_node(fail_id, "Failure", f"{episode.failure_count} Process Failures", {"count": episode.failure_count})
            self.add_edge(ep_node_id, fail_id, "CAUSES_FAILURE", float(episode.failure_count))

        # Trace preceding events
        prev_app_id = None
        for evt in events:
            if evt.application:
                cur_app_id = f"app:{evt.application}"
                if prev_app_id and prev_app_id != cur_app_id:
                    self.add_edge(prev_app_id, cur_app_id, "TRANSITIONS_TO", 1.0)
                prev_app_id = cur_app_id

    def query_preceding_activity(self, target_type: str = "Failure") -> List[Dict[str, Any]]:
        """Finds activity patterns that normally precede a crash or failure."""
        preceding_apps: Set[str] = set()
        preceding_episodes: List[str] = []

        target_nodes = [nid for nid, data in self.nodes.items() if data["type"] == target_type]
        for t_id in target_nodes:
            for src, tgt, rel, w in self.edges:
                if tgt == t_id and rel == "CAUSES_FAILURE":
                    preceding_episodes.append(src)
                    # Find apps used in that episode
                    for s_app, t_app, rel_app, _ in self.edges:
                        if s_app == src and rel_app == "USES_APP":
                            preceding_apps.add(self.nodes[t_app]["label"])

        return {
            "target": target_type,
            "associated_episodes": preceding_episodes,
            "preceding_applications": list(preceding_apps),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": list(self.nodes.values()),
            "edges": [
                {"source": s, "target": t, "rel_type": r, "weight": w}
                for s, t, r, w in self.edges
            ]
        }
