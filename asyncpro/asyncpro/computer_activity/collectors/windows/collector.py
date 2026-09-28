"""
Windows Telemetry Collector implementation.
"""
from typing import List
import psutil
from computer_activity.core.domain.events import CanonicalEvent, EventPriority, ProcessIdentity


class WindowsCollector:
    """Windows platform collector using psutil and Win32 process tracking."""

    def __init__(self):
        self._known_pids = set()

    def collect_process_events(self) -> List[CanonicalEvent]:
        events = []
        current_pids = set()

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
            try:
                pid = proc.info['pid']
                current_pids.add(pid)
                name = proc.info['name'] or "unknown"
                exe = proc.info['exe'] or name
                create_time = str(proc.info['create_time'])

                if pid not in self._known_pids:
                    proc_identity = ProcessIdentity(pid=pid, start_time=create_time, executable=exe, name=name)
                    evt = CanonicalEvent(
                        platform="windows",
                        collector="process",
                        event_type="process.started",
                        process=proc_identity,
                        application=name,
                        resource=exe,
                        priority=EventPriority.MEDIUM,
                    )
                    events.append(evt)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        self._known_pids = current_pids
        return events

    def collect_window_events(self) -> List[CanonicalEvent]:
        return []

    def collect_file_events(self) -> List[CanonicalEvent]:
        return []

    def collect_system_metrics(self) -> List[CanonicalEvent]:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        return [CanonicalEvent(
            platform="windows",
            collector="system",
            event_type="system.metrics",
            application="system",
            metadata={"cpu_percent": cpu, "memory_percent": mem.percent},
            priority=EventPriority.LOW
        )]

    def collect_network_metadata(self) -> List[CanonicalEvent]:
        return []
