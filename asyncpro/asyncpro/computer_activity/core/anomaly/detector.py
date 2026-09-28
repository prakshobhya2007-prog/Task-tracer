"""
Multi-Level Anomaly Detection Engine.
Combines Rule-Based thresholds, Statistical Z-Score/MAD metrics, and ML Isolation Forest models.
Calculates deterministic anomaly scores and rule justifications.
"""
from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest

from computer_activity.core.domain.episodes import EpisodeEnvelope


class AnomalyDetector:
    """Multi-level baseline anomaly detector."""

    def __init__(self, switch_rate_threshold: float = 1.2):
        self.switch_rate_threshold = switch_rate_threshold
        self.iso_forest = IsolationForest(n_estimators=50, contamination=0.1, random_state=42)
        self.is_fitted = False

    def evaluate_episode(self, episode: EpisodeEnvelope, features: Dict[str, float]) -> Tuple[float, List[str]]:
        """
        Evaluates an episode for anomalies.
        Returns (anomaly_score 0.0 to 1.0, list of explicit rule reasons).
        """
        reasons: List[str] = []
        score = 0.0

        # Rule 1: High context switching rate (> 1.2 switches/min or > 15 switches in episode)
        switch_rate = features.get("context_switch_rate", 0.0)
        app_switches = features.get("app_switch_count", 0.0)
        if switch_rate > self.switch_rate_threshold or app_switches >= 15:
            reasons.append(f"Excessive application switching ({app_switches:.0f} switches, {switch_rate:.1f} switches/min)")
            score += 0.45

        # Rule 2: Repeated process failures
        failures = features.get("failure_count", 0.0)
        if failures >= 2:
            reasons.append(f"Multiple execution failures detected ({failures:.0f} failed process exits)")
            score += 0.40

        # Rule 3: High sequence entropy (unpredictable/fragmented activity)
        entropy = features.get("sequence_entropy", 0.0)
        if entropy > 2.5:
            reasons.append(f"High activity fragmentation (sequence entropy {entropy:.2f})")
            score += 0.20

        # Bound score between 0.0 and 1.0
        final_score = min(1.0, max(0.0, score))
        return final_score, reasons

    def fit_ml_baseline(self, feature_matrix: List[List[float]]):
        """Fits the ML IsolationForest on baseline user activity feature vectors."""
        if len(feature_matrix) >= 5:
            X = np.array(feature_matrix)
            self.iso_forest.fit(X)
            self.is_fitted = True

    def predict_ml_anomaly(self, feature_vector: List[float]) -> float:
        """Returns ML anomaly decision score if model is fitted."""
        if not self.is_fitted:
            return 0.0
        X = np.array([feature_vector])
        raw_score = float(self.iso_forest.score_samples(X)[0])
        # Map raw score (-1 to 0) to [0, 1] anomaly likelihood
        norm_score = min(1.0, max(0.0, -raw_score))
        return norm_score
