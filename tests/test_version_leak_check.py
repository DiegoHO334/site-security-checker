"""Tests for check_version_leak, using the same mocking approach as
test_headers_check.py.
"""

from unittest.mock import patch

import requests

from checks.version_leak_check import check_version_leak


def _fake_response(headers: dict) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response.headers.update(headers)
    return response


@patch("checks.version_leak_check.requests.get")
def test_no_headers_means_no_leak(mock_get):
    mock_get.return_value = _fake_response({})

    result = check_version_leak("https://example.com")

    assert result["leaks"] == []


@patch("checks.version_leak_check.requests.get")
def test_bare_software_name_is_not_flagged_as_leak(mock_get):
    # "cloudflare" or "nginx" with no digits names the software but
    # not a version -- less useful to an attacker than a full version
    # string, so our check treats it as not a leak.
    mock_get.return_value = _fake_response({"Server": "nginx"})

    result = check_version_leak("https://example.com")

    assert result["leaks"] == []
    assert result["headers"]["Server"] == "nginx"


@patch("checks.version_leak_check.requests.get")
def test_version_number_is_flagged_as_leak(mock_get):
    mock_get.return_value = _fake_response({"Server": "nginx/1.18.0"})

    result = check_version_leak("https://example.com")

    assert result["leaks"] == ["Server"]


@patch("checks.version_leak_check.requests.get")
def test_both_headers_can_leak_independently(mock_get):
    mock_get.return_value = _fake_response({
        "Server": "Apache/2.4.41",
        "X-Powered-By": "PHP/8.1.2",
    })

    result = check_version_leak("https://example.com")

    assert set(result["leaks"]) == {"Server", "X-Powered-By"}
