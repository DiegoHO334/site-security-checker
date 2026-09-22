"""Test for generate_report/format_report.

Here we mock one level higher than the other tests: instead of faking
the network, we fake the three check_* functions themselves. report.py
doesn't care *how* those functions get their answers, only that it
calls all three and passes the results to calculate_score -- so that's
what this test verifies, without needing to know anything about
sockets or requests.
"""

from unittest.mock import patch

from report import generate_report, format_report


@patch("report.check_version_leak")
@patch("report.check_headers")
@patch("report.check_https")
def test_generate_report_combines_all_three_checks(mock_https, mock_headers, mock_version):
    mock_https.return_value = {
        "url": "https://example.com",
        "uses_https": True,
        "cert_valid": True,
        "days_until_expiry": 90,
        "error": None,
    }
    mock_headers.return_value = {
        "url": "https://example.com",
        "headers": {"Strict-Transport-Security": "max-age=1"},
        "missing": [],
        "error": None,
    }
    mock_version.return_value = {
        "url": "https://example.com",
        "headers": {"Server": None, "X-Powered-By": None},
        "leaks": [],
        "error": None,
    }

    report = generate_report("https://example.com")

    assert report["url"] == "https://example.com"
    assert report["score"]["https_score"] == 40
    # format_report should run without raising on a real report shape
    text = format_report(report)
    assert "https://example.com" in text
    assert "Score:" in text
