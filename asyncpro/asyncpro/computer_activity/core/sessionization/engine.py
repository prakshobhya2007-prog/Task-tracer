"""
Deterministic Sessionization & Episode Engine.
Transforms stream of canonical events into explainable activity episodes.
"""
from typing import List, Optional
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.episodes import EpisodeEnvelope


class Sessionizer:
    """
    Sessionization engine partitioning events into episodes based on
    inactivity gaps, workspace boundaries, and focus transitions.
    """

    def __init__(self, gap_threshold_seconds: float = 300.0):
        self.gap_threshold_seconds = gap_threshold_seconds

    def sessionize(self, events: List[CanonicalEvent]) -> List[EpisodeEnvelope]:
        """Partitions an ordered list of events into discrete EpisodeEnvelopes."""
        if not events:
            return []

        sorted_events = sorted(events, key=lambda e: e.monotonic_timestamp)
        episodes: List[EpisodeEnvelope] = []
        current_ep: Optional[EpisodeEnvelope] = None

        last_mono: float = sorted_events[0].monotonic_timestamp
        last_app: str = ""

        for evt in sorted_events:
            gap = evt.monotonic_timestamp - last_mono

            # Determine if a new episode boundary should be triggered
            trigger_new = False
            boundary_reason = ""

            if current_ep is None:
                trigger_new = True
                boundary_reason = "Initial episode"
            elif gap > self.gap_threshold_seconds:
                trigger_new = True
                boundary_reason = f"Inactivity gap of {gap:.1f}s exceeded threshold ({self.gap_threshold_seconds}s)"

            if trigger_new:
                if current_ep:
                    current_ep.end_time = last_evt.timestamp
                    current_ep.end_monotonic = last_evt.monotonic_timestamp
                    episodes.append(current_ep)

                current_ep = EpisodeEnvelope(
                    start_time=evt.timestamp,
                    start_monotonic=evt.monotonic_timestamp,
                    metadata={"boundary_reason": boundary_reason}
                )

            # Update current episode with event details
            current_ep.event_ids.append(evt.event_id)

            if evt.application and evt.application not in current_ep.applications:
                current_ep.applications.append(evt.application)

            if evt.resource:
                if evt.collector == "filesystem" and evt.resource not in current_ep.files:
                    current_ep.files.append(evt.resource)
                elif evt.collector == "browser" and evt.resource not in current_ep.domains:
                    current_ep.domains.append(evt.resource)

            if evt.process and evt.process.name and evt.process.name not in current_ep.processes:
                current_ep.processes.append(evt.process.name)

            # Action sequence tracking
            action = f"{evt.collector}:{evt.event_type}:{evt.application}"
            current_ep.action_sequence.append(action)

            # Switch count
            if last_app and evt.application != last_app:
                current_ep.switch_count += 1
            last_app = evt.application

            # Process success / failure counters
            if evt.event_type == "process.exited":
                exit_code = evt.metadata.get("exit_code", 0)
                if exit_code == 0:
                    current_ep.success_count += 1
                else:
                    current_ep.failure_count += 1

            last_mono = evt.monotonic_timestamp
            last_evt = evt

        if current_ep:
            current_ep.end_time = sorted_events[-1].timestamp
            current_ep.end_monotonic = sorted_events[-1].monotonic_timestamp
            episodes.append(current_ep)

        return episodes
