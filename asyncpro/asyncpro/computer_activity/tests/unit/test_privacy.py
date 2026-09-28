"""
Unit tests for Privacy Firewall and User Controls.
"""
from computer_activity.core.domain.events import CanonicalEvent, PrivacyClass
from computer_activity.core.privacy.firewall import PrivacyFirewall


def test_forbidden_telemetry_dropped():
    fw = PrivacyFirewall()
    forbidden_evt = CanonicalEvent(
        collector="keystroke",
        event_type="keystroke.press",
        application="VS Code",
    )
    res = fw.process_event(forbidden_evt)
    assert res is None


def test_pause_toggle_drops_all_events():
    fw = PrivacyFirewall()
    fw.update_settings(is_paused=True)

    evt = CanonicalEvent(collector="process", event_type="process.started", application="VS Code")
    res = fw.process_event(evt)
    assert res is None


def test_excluded_application_dropped():
    fw = PrivacyFirewall()
    fw.update_settings(excluded_applications=["slack", "spotify"])

    evt = CanonicalEvent(collector="process", application="Slack")
    assert fw.process_event(evt) is None

    safe_evt = CanonicalEvent(collector="process", application="VS Code")
    assert fw.process_event(safe_evt) is not None


def test_browser_url_sanitized_to_domain():
    fw = PrivacyFirewall()
    browser_evt = CanonicalEvent(
        collector="browser",
        event_type="browser.navigated",
        application="Chrome",
        resource="https://github.com/org/repo/issues/123?token=secret123",
    )
    processed = fw.process_event(browser_evt)
    assert processed is not None
    assert processed.resource == "github.com"
