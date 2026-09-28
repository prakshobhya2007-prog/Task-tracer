"""
macOS Telemetry Collector Adapter.
"""
from typing import List
from computer_activity.core.domain.events import CanonicalEvent


class MacOSCollector:
    """macOS platform collector stub / adapter."""

    def collect_process_events(self) -> List[CanonicalEvent]:
        return []

    def collect_window_events(self) -> List[CanonicalEvent]:
        return []

    def collect_file_events(self) -> List[CanonicalEvent]:
        return []

    def collect_system_metrics(self) -> List[CanonicalEvent]:
        return []

    def collect_network_metadata(self) -> List[CanonicalEvent]:
        return []
