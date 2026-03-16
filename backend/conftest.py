"""Pytest configuration — project-wide fixtures and session setup."""

import sys


def pytest_configure(config):  # noqa: ANN001, ANN201
    """Ensure stdout/stderr use UTF-8 on Windows (cp1252 cannot encode → etc.)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
