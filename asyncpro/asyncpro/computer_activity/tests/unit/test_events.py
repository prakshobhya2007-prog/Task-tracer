"""
Unit tests for Canonical Event Model and Process Identity.
"""
from computer_activity.core.domain.events import CanonicalEvent, EventPriority, PrivacyClass, ProcessIdentity


def test_process_identity_hashing():
    p1 = ProcessIdentity(pid=1234, start_time="1000", executable="/usr/bin/gcc", name="gcc")
    p2 = ProcessIdentity(pid=1234, start_time="1000", executable="/usr/bin/gcc", name="gcc")
    p3 = ProcessIdentity(pid=5678, start_time="2000", executable="/usr/bin/gcc", name="gcc")

    assert p1.instance_id == p2.instance_id
    assert p1.instance_id != p3.instance_id


def test_canonical_event_serialization():
    proc = ProcessIdentity(pid=99, start_time="500", executable="app", name="app")
    evt = CanonicalEvent(
        platform="linux",
        collector="process",
        event_type="process.started",
        process=proc,
        application="app",
        resource="res",
        priority=EventPriority.HIGH,
    )

    data = evt.to_dict()
    assert data["event_type"] == "process.started"
    assert data["priority"] == "HIGH"
    assert data["process"]["pid"] == 99

    reconstructed = CanonicalEvent.from_dict(data)
    assert reconstructed.event_id == evt.event_id
    assert reconstructed.process.pid == 99
