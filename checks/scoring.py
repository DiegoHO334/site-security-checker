"""Turns the results of the individual checks into a single 0-100 score.

Kept separate from the checks themselves (https_check, headers_check,
version_leak_check) so each check's job stays simple: "go find out X
about this site." Deciding how much each finding is *worth* is a
different concern, and living here means we can tune the weights
without touching any networking code.
"""

HTTPS_POINTS = 40
HEADERS_POINTS = 35
VERSION_POINTS = 25


def calculate_score(https_result: dict, headers_result: dict, version_result: dict) -> dict:
    """Combine the three check results into a score out of 100.

    Weighting (out of 100):
      - HTTPS + valid certificate: 40 points
      - Security headers present:  35 points, split evenly per header
      - No version leaks:          25 points, split evenly per header
    """
    https_score = 0
    if https_result["uses_https"]:
        https_score += HTTPS_POINTS // 2
    if https_result["cert_valid"]:
        https_score += HTTPS_POINTS // 2

    total_headers = len(headers_result["headers"])
    headers_present = total_headers - len(headers_result["missing"])
    headers_score = round(HEADERS_POINTS * headers_present / total_headers)

    total_version_headers = len(version_result["headers"])
    leaks = len(version_result["leaks"])
    version_score = round(VERSION_POINTS * (total_version_headers - leaks) / total_version_headers)

    total = https_score + headers_score + version_score

    return {
        "total": total,
        "https_score": https_score,
        "https_max": HTTPS_POINTS,
        "headers_score": headers_score,
        "headers_max": HEADERS_POINTS,
        "version_score": version_score,
        "version_max": VERSION_POINTS,
        "grade": _grade_for(total),
    }


def _grade_for(total: int) -> str:
    """Simple letter grade so the score means something at a glance."""
    if total >= 90:
        return "A"
    if total >= 80:
        return "B"
    if total >= 70:
        return "C"
    if total >= 60:
        return "D"
    return "F"
