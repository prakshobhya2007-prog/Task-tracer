"""
Unit tests for Secret & Path Redaction Utilities.
"""
from computer_activity.security.redaction.redactor import Redactor


def test_bearer_token_redaction():
    text = "curl https://api.example.com -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'"
    sanitized = Redactor.sanitize_text(text)
    assert "Bearer [REDACTED_TOKEN]" in sanitized
    assert "eyJ" not in sanitized


def test_sensitive_path_redaction():
    home_secret = "/home/user/private/secrets/db_password.txt"
    sanitized = Redactor.sanitize_path(home_secret)
    assert "[sensitive-file]" in sanitized or "~/" in sanitized
