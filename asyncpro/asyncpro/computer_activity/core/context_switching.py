"""
Context-Switching & Focus Fragmentation Analysis Engine.
Calculates fragmentation score, dwell times, transition entropy, and re-entry frequency.
"""
from typing import Dict, List
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.episodes import EpisodeEnvelope


class ContextSwitchingAnalyzer:
    """Analyzes user focus transitions and context fragmentation."""

    @staticmethod
    def analyze_episode(episode: EpisodeEnvelope, events: List[CanonicalEvent]) -> Dict[str, float]:
        app_dwell_times: Dict[str, float] = {}
        last_app = None
        last_mono = episode.start_monotonic

        for evt in events:
            if evt.application:
                if last_app:
                    delta = max(0.0, evt.monotonic_timestamp - last_mono)
                    app_dwell_times[last_app] = app_dwell_times.get(last_app, 0.0) + delta
                last_app = evt.application
                last_mono = evt.monotonic_timestamp

        total_dwell = sum(app_dwell_times.values())
        mean_dwell = (total_dwell / len(app_dwell_times)) if app_dwell_times else 0.0
        
        # Fragmentation score normalized 0.0 to 1.0 (high switch count + low mean dwell time)
        duration_mins = max(1.0, (episode.end_monotonic - episode.start_monotonic) / 60.0) if episode.end_monotonic else 1.0
        switch_rate = episode.switch_count / duration_mins

        fragmentation_score = min(1.0, (switch_rate / 3.0) + (1.0 if mean_dwell < 15.0 and episode.switch_count > 5 else 0.0))

        return {
            "mean_dwell_seconds": float(mean_dwell),
            "context_switch_rate_per_min": float(switch_rate),
            "fragmentation_score": float(fragmentation_score),
            "re_entry_frequency": float(episode.switch_count / max(1, len(episode.applications))),
        }
