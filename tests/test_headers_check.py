"""Tests for check_headers.

check_headers calls the real network via requests.get(). A real test
suite must NOT depend on the network -- it would be slow, it would
fail if you're offline or the test site changes, and it's not testing
*our* code, it's testing the internet. So we use unittest.mock.patch
to replace requests.get with a fake version we control, and assert
that check_headers reacts correctly to whatever that fake returns.

This is "mocking": swapping a real dependency for a fake stand-in
during a test, so the test is fast, repeatable, and isolated.
"""

from unittest.mock import patch

import requests

from checks.headers_check import check_headers


def _fake_response(headers: dict) -> requests.Response:
    """Build a real requests.Response object with fake headers, so
    check_headers sees the same shape of object it would in production
    (response.headers behaves like a real CaseInsensitiveDict).
    """
    response = requests.Response()
    response.status_code = 200
    response.headers.update(headers)
    return response


@patch("checks.headers_check.requests.get")
def test_all_headers_present(mock_get):
    mock_get.return_value = _fake_response({
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    })

    result = check_headers("https://example.com")

    assert result["missing"] == []
    assert result["headers"]["X-Frame-Options"] == "DENY"
    assert result["error"] is None


@patch("checks.headers_check.requests.get")
def test_missing_headers_are_reported(mock_get):
    mock_get.return_value = _fake_response({})

    result = check_headers("https://example.com")

    assert len(result["missing"]) == 5
    assert all(value is None for value in result["headers"].values())


@patch("checks.headers_check.requests.get")
def test_header_lookup_is_case_insensitive(mock_get):
    # Servers can send headers in any casing; HTTP headers are
    # case-insensitive by spec, so "content-security-policy" (all
    # lowercase) must still be found.
    mock_get.return_value = _fake_response({"content-security-policy": "default-src 'self'"})

    result = check_headers("https://example.com")

    assert result["headers"]["Content-Security-Policy"] == "default-src 'self'"


@patch("checks.headers_check.requests.get")
def test_connection_failure_is_reported_not_raised(mock_get):
    # side_effect makes the mock raise instead of returning a value,
    # simulating a real network failure (DNS error, timeout, etc.)
    mock_get.side_effect = requests.exceptions.ConnectionError("name resolution failed")

    result = check_headers("https://does-not-exist.invalid")

    assert result["error"] is not None
    assert len(result["missing"]) == 5
