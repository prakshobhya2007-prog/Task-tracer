"""
Privacy Firewall Engine.
Filters, redacts, hashes, or drops raw events BEFORE they are saved to SQLite or exposed to AI.
Enforces privacy classifications and user privacy preferences.
"""
from typing import List, Optional, Set
from computer_activity.core.domain.events import CanonicalEvent, EventPriority, PrivacyClass, RedactionStatus
from computer_activity.security.redaction.redactor import Redactor


# Forbidden event types or telemetry categories that must NEVER be collected
FORBIDDEN_COLLECTORS_OR_TYPES = {
    "keystroke", "keylogger", "clipboard", "screenshot", "camera",
    "microphone", "browser.raw_content", "form_content", "env_vars"
}


class PrivacyFirewall:
    """Privacy Firewall evaluating and transforming events before storage."""

    def __init__(self):
        self.is_paused: bool = False
        self.excluded_applications: Set[str] = set()
        self.excluded_directories: Set[str] = set()
        self.excluded_domains: Set[str] = set()
        self.disabled_categories: Set[str] = set()

    def update_settings(
        self,
        is_paused: Optional[bool] = None,
        excluded_applications: Optional[List[str]] = None,
        excluded_directories: Optional[List[str]] = None,
        excluded_domains: Optional[List[str]] = None,
        disabled_categories: Optional[List[str]] = None,
    ):
        if is_paused is not None:
            self.is_paused = is_paused
        if excluded_applications is not None:
            self.excluded_applications = set(app.lower() for app in excluded_applications)
        if excluded_directories is not None:
            self.excluded_directories = set(d.lower() for d in excluded_directories)
        if excluded_domains is not None:
            self.excluded_domains = set(dom.lower() for dom in excluded_domains)
        if disabled_categories is not None:
            self.disabled_categories = set(cat.lower() for cat in disabled_categories)

    def process_event(self, event: CanonicalEvent) -> Optional[CanonicalEvent]:
        """
        Processes a raw canonical event.
        Returns transformed safe CanonicalEvent, or None if event is dropped.
        """
        # 1. Global pause check
        if self.is_paused:
            return None

        # 2. Check forbidden categories or event types
        if (
            event.collector.lower() in FORBIDDEN_COLLECTORS_OR_TYPES
            or any(f in event.event_type.lower() for f in FORBIDDEN_COLLECTORS_OR_TYPES)
        ):
            event.privacy_class = PrivacyClass.FORBIDDEN
            event.redaction_status = RedactionStatus.DISCARDED
            return None

        # 3. Check disabled telemetry categories
        if event.collector.lower() in self.disabled_categories:
            return None

        # 4. Check user exclusion rules
        if event.application and event.application.lower() in self.excluded_applications:
            return None

        if event.resource:
            res_lower = event.resource.lower()
            if any(exc_dir in res_lower for exc_dir in self.excluded_directories):
                return None
            if any(exc_dom in res_lower for exc_dom in self.excluded_domains):
                return None

        # 5. Apply privacy classification and redaction
        classified_event = self._classify_and_redact(event)
        
        # If classified as SECRET or FORBIDDEN, drop it completely
        if classified_event.privacy_class in (PrivacyClass.SECRET, PrivacyClass.FORBIDDEN):
            return None

        return classified_event

    def _classify_and_redact(self, event: CanonicalEvent) -> CanonicalEvent:
        """Applies field-level classification and sanitization."""
        # Sanitize metadata dict for secrets
        if event.metadata:
            event.metadata = Redactor.sanitize_dict(event.metadata)
            event.redaction_status = RedactionStatus.REDACTED

        # Resource sanitization (paths, URLs, commands)
        if event.resource:
            if event.collector == "browser":
                # For browser URLs, extract registrable domain only, drop query params/tokens
                domain = self._extract_domain(event.resource)
                event.resource = domain
                event.privacy_class = PrivacyClass.PERSONAL_METADATA
                event.redaction_status = RedactionStatus.REDACTED
            elif event.collector == "terminal":
                # Sanitize command text
                event.resource = Redactor.sanitize_text(event.resource)
                event.privacy_class = PrivacyClass.SENSITIVE_METADATA
                event.redaction_status = RedactionStatus.REDACTED
            elif event.collector == "filesystem" or "/" in event.resource or "\\" in event.resource:
                event.resource = Redactor.sanitize_path(event.resource)
                event.privacy_class = PrivacyClass.PERSONAL_METADATA
                event.redaction_status = RedactionStatus.REDACTED

        # Default classification if not set
        if not event.privacy_class or event.privacy_class == PrivacyClass.PUBLIC_METADATA:
            if event.collector in ["process", "system", "window"]:
                event.privacy_class = PrivacyClass.PUBLIC_METADATA
            else:
                event.privacy_class = PrivacyClass.PERSONAL_METADATA

        return event

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Scrubs complete URL to extract registrable domain only."""
        if not url:
            return ""
        clean = url.replace("https://", "").replace("http://", "").split("/")[0].split("?")[0]
        return clean
