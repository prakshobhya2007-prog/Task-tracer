"""
Platform Collector Protocol / Abstract Base Class.
Defines the standard cross-platform interface for OS activity telemetry collectors.
"""
from typing import List, Protocol
from computer_activity.core.domain.events import CanonicalEvent


class PlatformCollector(Protocol):
    """Protocol defining standard platform telemetry collection capabilities."""

    def collect_process_events(self) -> List[CanonicalEvent]:
        ...

    def collect_window_events(self) -> List[CanonicalEvent]:
        ...

    def collect_file_events(self) -> List[CanonicalEvent]:
        ...

    def collect_system_metrics(self) -> List[CanonicalEvent]:
        ...

    def collect_network_metadata(self) -> List[CanonicalEvent]:
        ...
