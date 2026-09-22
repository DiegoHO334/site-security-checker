"""Tests for check_https.

This one is trickier to mock than the requests-based checks: instead
of one function call (requests.get), check_https makes a raw socket
connection and then a separate TLS handshake. We mock both pieces:

  - socket.create_connection -- normally opens a real TCP connection.
    We replace it with a MagicMock configured to behave like the
    `with socket.create_connection(...) as sock:` context manager,
    but without touching the network.
  - ssl.create_default_context -- normally returns a real SSLContext
    that does real certificate verification. We replace it with a
    MagicMock whose wrap_socket() returns a fake TLS socket whose
    getpeercert() returns whatever certificate data we want to test
    against (e.g. one that expires soon, one that's invalid, etc.)

This lets us test "what does check_https do with a cert that expires
in 10 days" without needing a real server holding that exact cert.
"""

import ssl
from unittest.mock import MagicMock, patch

from checks.https_check import check_https


def test_http_url_is_reported_as_not_using_https():
    # No mocking needed here -- check_https returns early for
    # non-https URLs, before it ever touches a socket.
    result = check_https("http://example.com")

    assert result["uses_https"] is False
    assert result["cert_valid"] is None


@patch("checks.https_check.ssl.create_default_context")
@patch("checks.https_check.socket.create_connection")
def test_valid_certificate_reports_days_until_expiry(mock_create_connection, mock_create_context):
    mock_sock = MagicMock()
    mock_create_connection.return_value.__enter__.return_value = mock_sock

    mock_ssock = MagicMock()
    mock_ssock.getpeercert.return_value = {"notAfter": "Jan 1 00:00:00 2099 GMT"}
    mock_create_context.return_value.wrap_socket.return_value.__enter__.return_value = mock_ssock

    result = check_https("https://example.com")

    assert result["uses_https"] is True
    assert result["cert_valid"] is True
    assert result["days_until_expiry"] > 0
    assert result["error"] is None


@patch("checks.https_check.ssl.create_default_context")
@patch("checks.https_check.socket.create_connection")
def test_failed_verification_reports_cert_invalid(mock_create_connection, mock_create_context):
    error = ssl.SSLCertVerificationError("certificate verify failed")
    error.verify_message = "certificate has expired"
    mock_create_context.return_value.wrap_socket.side_effect = error

    result = check_https("https://example.com")

    assert result["uses_https"] is True
    assert result["cert_valid"] is False
    assert "certificate has expired" in result["error"]


@patch("checks.https_check.ssl.create_default_context")
@patch("checks.https_check.socket.create_connection")
def test_unreachable_host_is_reported_not_raised(mock_create_connection, mock_create_context):
    import socket

    mock_create_connection.side_effect = socket.gaierror("name or service not known")

    result = check_https("https://does-not-exist.invalid")

    assert result["cert_valid"] is None
    assert result["error"] is not None
