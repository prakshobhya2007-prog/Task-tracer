"""
Secret and Path Redaction Utilities.
Redacts passwords, tokens, API keys, private filesystem paths, and auth headers.
"""
import os
import re
from typing import Any, Dict


# Regex patterns for common secrets
SECRET_PATTERNS = [
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9\-\._~\+\/]+=*"), r"\1[REDACTED_TOKEN]"),
    (re.compile(r"(?i)(api[_\-]?key\s*[:=]\s*)[A-Za-z0-9\-_]+"), r"\1[REDACTED_API_KEY]"),
    (re.compile(r"(?i)(password\s*[:=]\s*)[^\s&]+"), r"\1[REDACTED_PASSWORD]"),
    (re.compile(r"(?i)(secret\s*[:=]\s*)[^\s&]+"), r"\1[REDACTED_SECRET]"),
    (re.compile(r"eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_=]*"), "[REDACTED_JWT]"),
    (re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,12}-[0-9a-zA-Z]{10,12}-[a-zA-Z0-9]{24,32}"), "[REDACTED_SLACK_TOKEN]"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "[REDACTED_GITHUB_TOKEN]"),
]


class Redactor:
    """Central redaction engine for scrubbing telemetry and text."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text:
            return ""
        result = text
        for pattern, replacement in SECRET_PATTERNS:
            result = pattern.sub(replacement, result)
        return result

    @staticmethod
    def sanitize_path(path_str: str) -> str:
        """Converts absolute user paths into privacy-safe sanitized paths."""
        if not path_str:
            return ""
        
        # Replace home directory with ~
        home = os.path.expanduser("~")
        if home and path_str.startswith(home):
            relative = path_str[len(home):].lstrip("/\\")
            parts = relative.replace("\\", "/").split("/")
            if len(parts) > 1 and parts[0] in ["private", "secrets", "confidential", ".ssh", ".aws", ".gnupg"]:
                return f"~/{parts[0]}/[sensitive-file]"
            return f"~/{relative}"
        
        # Check for generic sensitive folders
        normalized = path_str.replace("\\", "/")
        if any(seg in normalized.lower() for seg in ["/secrets/", "/private/", "/.ssh/", "/.aws/"]):
            return ".../[sensitive-file]"
            
        return path_str

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitizes dictionary values."""
        clean = {}
        for key, val in data.items():
            key_lower = key.lower()
            if any(s in key_lower for s in ["password", "token", "secret", "auth", "credential", "private_key"]):
                clean[key] = "[REDACTED]"
            elif isinstance(val, str):
                clean[key] = cls.sanitize_text(val)
            elif isinstance(val, dict):
                clean[key] = cls.sanitize_dict(val)
            elif isinstance(val, list):
                clean[key] = [
                    cls.sanitize_dict(item) if isinstance(item, dict)
                    else (cls.sanitize_text(item) if isinstance(item, str) else item)
                    for item in val
                ]
            else:
                clean[key] = val
        return clean
