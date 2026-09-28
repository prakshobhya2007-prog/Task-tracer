"""
Deterministic Feature Extraction Engine.
Extracts numerical metrics from activity episodes.
"""
import math
from typing import Dict, List
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.episodes import EpisodeEnvelope


class FeatureExtractor:
    """Computes deterministic features from episodes and events."""

    @staticmethod
    def extract_features(episode: EpisodeEnvelope, events: List[CanonicalEvent]) -> Dict[str, float]:
        duration = 0.0
        if episode.end_monotonic and episode.start_monotonic:
            duration = max(0.0, episode.end_monotonic - episode.start_monotonic)

        app_switch_count = episode.switch_count
        unique_apps = len(episode.applications)
        unique_files = len(episode.files)
        unique_domains = len(episode.domains)
        failures = episode.failure_count
        successes = episode.success_count

        total_procs = failures + successes
        failure_rate = (failures / total_procs) if total_procs > 0 else 0.0

        # Calculate Shannon entropy of action sequence
        entropy = 0.0
        if episode.action_sequence:
            freq: Dict[str, int] = {}
            for act in episode.action_sequence:
                freq[act] = freq.get(act, 0) + 1
            total = len(episode.action_sequence)
            for cnt in freq.values():
                p = cnt / total
                entropy -= p * math.log2(p)

        # CPU/RAM metrics if available in events
        cpu_vals = [e.metadata["cpu_percent"] for e in events if "cpu_percent" in e.metadata]
        ram_vals = [e.metadata["memory_percent"] for e in events if "memory_percent" in e.metadata]

        cpu_avg = sum(cpu_vals) / len(cpu_vals) if cpu_vals else 0.0
        cpu_peak = max(cpu_vals) if cpu_vals else 0.0
        ram_avg = sum(ram_vals) / len(ram_vals) if ram_vals else 0.0

        context_switch_rate = (app_switch_count / (duration / 60.0)) if duration > 0 else 0.0

        return {
            "duration_seconds": float(duration),
            "app_switch_count": float(app_switch_count),
            "unique_apps_count": float(unique_apps),
            "unique_files_count": float(unique_files),
            "unique_domains_count": float(unique_domains),
            "failure_count": float(failures),
            "success_count": float(successes),
            "failure_rate": float(failure_rate),
            "sequence_entropy": float(entropy),
            "context_switch_rate": float(context_switch_rate),
            "cpu_avg_percent": float(cpu_avg),
            "cpu_peak_percent": float(cpu_peak),
            "ram_avg_percent": float(ram_avg),
        }
