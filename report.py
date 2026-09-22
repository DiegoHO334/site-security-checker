"""Runs all checks against a URL and formats a combined report."""

from checks.https_check import check_https
from checks.headers_check import check_headers
from checks.version_leak_check import check_version_leak
from checks.scoring import calculate_score


def generate_report(url: str) -> dict:
    """Run every check against a URL and score the result.

    Returns a dict bundling each check's raw result plus the score, so
    callers (the CLI now, maybe a web view later) can format it however
    they like without re-running the checks.
    """
    https_result = check_https(url)
    headers_result = check_headers(url)
    version_result = check_version_leak(url)
    score = calculate_score(https_result, headers_result, version_result)

    return {
        "url": url,
        "https": https_result,
        "headers": headers_result,
        "version": version_result,
        "score": score,
    }


def format_report(report: dict) -> str:
    """Turn a report dict into a human-readable, printable string."""
    https_result = report["https"]
    headers_result = report["headers"]
    version_result = report["version"]
    score = report["score"]

    lines = []
    lines.append(f"Site Security Report for {report['url']}")
    lines.append("=" * 40)

    lines.append("")
    lines.append("HTTPS / Certificate")
    lines.append(f"  Uses HTTPS:        {https_result['uses_https']}")
    lines.append(f"  Certificate valid: {https_result['cert_valid']}")
    lines.append(f"  Days until expiry: {https_result['days_until_expiry']}")
    if https_result["error"]:
        lines.append(f"  Error:             {https_result['error']}")

    lines.append("")
    lines.append("Security Headers")
    for name, value in headers_result["headers"].items():
        lines.append(f"  {name}: {value if value is not None else 'MISSING'}")

    lines.append("")
    lines.append("Server Version Leaks")
    for name, value in version_result["headers"].items():
        flag = " (LEAK)" if name in version_result["leaks"] else ""
        lines.append(f"  {name}: {value if value is not None else 'not present'}{flag}")

    lines.append("")
    lines.append(
        f"Score: {score['total']}/100 (grade {score['grade']})  "
        f"[HTTPS {score['https_score']}/{score['https_max']}, "
        f"Headers {score['headers_score']}/{score['headers_max']}, "
        f"Version {score['version_score']}/{score['version_max']}]"
    )

    return "\n".join(lines)
