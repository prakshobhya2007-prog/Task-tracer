"""
Semantic Embeddings Provider.
Computes vector representations for episodes using TF-IDF and deterministic feature projections.
"""
import math
from typing import Dict, List
import numpy as np
from computer_activity.core.domain.episodes import EpisodeEnvelope


class EmbeddingsProvider:
    """Generates normalized vector embeddings for episodes."""

    def __init__(self, vector_dim: int = 16):
        self.vector_dim = vector_dim

    def generate_episode_embedding(self, episode: EpisodeEnvelope, features: Dict[str, float]) -> List[float]:
        """Maps an episode and its features into a normalized float embedding vector."""
        vec = np.zeros(self.vector_dim, dtype=np.float32)

        vec[0] = math.log1p(features.get("duration_seconds", 0.0)) / 10.0
        vec[1] = features.get("app_switch_count", 0.0) / 20.0
        vec[2] = features.get("unique_apps_count", 0.0) / 10.0
        vec[3] = features.get("unique_files_count", 0.0) / 10.0
        vec[4] = features.get("failure_count", 0.0) / 5.0
        vec[5] = features.get("success_count", 0.0) / 10.0
        vec[6] = features.get("failure_rate", 0.0)
        vec[7] = features.get("sequence_entropy", 0.0) / 3.0
        vec[8] = features.get("context_switch_rate", 0.0) / 5.0

        # Encode applications into embedding dimensions 9..12 via simple hashing
        for app in episode.applications:
            h = hash(app) % 4
            vec[9 + h] += 0.5

        # Normalize vector
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        a = np.array(v1)
        b = np.array(v2)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
