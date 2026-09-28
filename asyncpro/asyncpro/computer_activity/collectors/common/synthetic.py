"""
Synthetic Event Generator & Scenario Replay Engine.
Generates deterministic synthetic event sequences for offline testing and hackathon demonstrations.
Supports scenarios like C++ debugging loop, rapid context switching, research loops, and normal coding.
"""
from datetime import datetime, timedelta, timezone
import time
from typing import List, Optional
from computer_activity.core.domain.events import CanonicalEvent, EventPriority, ProcessIdentity


class SyntheticEventGenerator:
    """Generates synthetic replay event sequences."""

    @staticmethod
    def generate_cpp_debugging_scenario() -> List[CanonicalEvent]:
        """
        Generates the standard C++ debugging loop scenario from Prompt § 40.
        VS Code -> edit main.cpp -> g++ -> exit 139 -> edit -> g++ -> exit 139 -> Chrome search -> VS Code
        """
        events: List[CanonicalEvent] = []
        base_time = datetime.now(timezone.utc) - timedelta(minutes=15)
        mono = time.monotonic() - 900.0

        proc_vscode = ProcessIdentity(pid=1001, start_time="0", executable="/usr/bin/code", name="VS Code")
        proc_gcc = ProcessIdentity(pid=1002, start_time="0", executable="/usr/bin/g++", name="g++")
        proc_app = ProcessIdentity(pid=1003, start_time="0", executable="./a.out", name="a.out")
        proc_chrome = ProcessIdentity(pid=1004, start_time="0", executable="/usr/bin/chrome", name="Chrome")

        # Step 1: Open VS Code
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=0)).isoformat(),
            monotonic_timestamp=mono + 0,
            collector="window", event_type="window.focused",
            process=proc_vscode, application="VS Code", priority=EventPriority.HIGH
        ))

        # Step 2: Edit main.cpp
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=15)).isoformat(),
            monotonic_timestamp=mono + 15,
            collector="filesystem", event_type="file.modified",
            process=proc_vscode, application="VS Code", resource="/home/user/project/main.cpp", priority=EventPriority.MEDIUM
        ))

        # Step 3: Compile g++
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=30)).isoformat(),
            monotonic_timestamp=mono + 30,
            collector="process", event_type="process.started",
            process=proc_gcc, application="g++", resource="/usr/bin/g++ main.cpp -o a.out", priority=EventPriority.MEDIUM
        ))

        # Step 4: Run a.out and crash (exit code 139)
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=45)).isoformat(),
            monotonic_timestamp=mono + 45,
            collector="process", event_type="process.exited",
            process=proc_app, application="a.out", metadata={"exit_code": 139}, priority=EventPriority.HIGH
        ))

        # Step 5: Edit main.cpp again
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=90)).isoformat(),
            monotonic_timestamp=mono + 90,
            collector="filesystem", event_type="file.modified",
            process=proc_vscode, application="VS Code", resource="/home/user/project/main.cpp", priority=EventPriority.MEDIUM
        ))

        # Step 6: Compile g++ again
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=105)).isoformat(),
            monotonic_timestamp=mono + 105,
            collector="process", event_type="process.started",
            process=proc_gcc, application="g++", resource="/usr/bin/g++ main.cpp -o a.out", priority=EventPriority.MEDIUM
        ))

        # Step 7: Run a.out and crash again (exit code 139)
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=120)).isoformat(),
            monotonic_timestamp=mono + 120,
            collector="process", event_type="process.exited",
            process=proc_app, application="a.out", metadata={"exit_code": 139}, priority=EventPriority.HIGH
        ))

        # Step 8: Open Chrome & search StackOverflow
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=150)).isoformat(),
            monotonic_timestamp=mono + 150,
            collector="window", event_type="window.focused",
            process=proc_chrome, application="Chrome", priority=EventPriority.HIGH
        ))
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=160)).isoformat(),
            monotonic_timestamp=mono + 160,
            collector="browser", event_type="browser.navigated",
            process=proc_chrome, application="Chrome", resource="https://stackoverflow.com/questions/segmentation-fault-c++", priority=EventPriority.MEDIUM
        ))

        # Step 9: Return to VS Code
        events.append(CanonicalEvent(
            timestamp=(base_time + timedelta(seconds=300)).isoformat(),
            monotonic_timestamp=mono + 300,
            collector="window", event_type="window.focused",
            process=proc_vscode, application="VS Code", priority=EventPriority.HIGH
        ))

        return events

    @staticmethod
    def generate_context_switching_scenario() -> List[CanonicalEvent]:
        """Generates 17 rapid application transitions within 14 minutes."""
        events: List[CanonicalEvent] = []
        base_time = datetime.now(timezone.utc) - timedelta(minutes=14)
        mono = time.monotonic() - 840.0

        apps = ["VS Code", "Chrome", "Terminal", "Slack", "Spotify"]
        for i in range(17):
            app = apps[i % len(apps)]
            events.append(CanonicalEvent(
                timestamp=(base_time + timedelta(seconds=i * 45)).isoformat(),
                monotonic_timestamp=mono + (i * 45),
                collector="window", event_type="window.focused",
                application=app, priority=EventPriority.HIGH
            ))
        return events
