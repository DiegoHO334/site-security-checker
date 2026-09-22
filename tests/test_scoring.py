"""Tests for calculate_score.

These don't touch the network at all -- calculate_score is a pure
function (same inputs always give the same output, no side effects),
so we just hand it fake check results and assert on the numbers. This
is the easiest kind of test to write and a good place to start.
"""

from checks.scoring import calculate_score

GOOD_HTTPS = {"uses_https": True, "cert_valid": True}
BAD_HTTPS = {"uses_https": False, "cert_valid": None}

ALL_HEADERS_PRESENT = {
    "headers": {
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    },
    "missing": [],
}

NO_HEADERS_PRESENT = {
    "headers": {
        "Strict-Transport-Security": None,
        "Content-Security-Policy": None,
        "X-Frame-Options": None,
        "X-Content-Type-Options": None,
        "Referrer-Policy": None,
    },
    "missing": [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
    ],
}

NO_VERSION_LEAKS = {
    "headers": {"Server": "nginx", "X-Powered-By": None},
    "leaks": [],
}

ONE_VERSION_LEAK = {
    "headers": {"Server": "nginx/1.18.0", "X-Powered-By": None},
    "leaks": ["Server"],
}


def test_perfect_site_scores_100_with_grade_a():
    score = calculate_score(GOOD_HTTPS, ALL_HEADERS_PRESENT, NO_VERSION_LEAKS)

    assert score["total"] == 100
    assert score["grade"] == "A"


def test_worst_case_scores_0_with_grade_f():
    both_leak = {"headers": {"Server": "nginx/1.2", "X-Powered-By": "PHP/8.1"}, "leaks": ["Server", "X-Powered-By"]}

    score = calculate_score(BAD_HTTPS, NO_HEADERS_PRESENT, both_leak)

    assert score["total"] == 0
    assert score["grade"] == "F"


def test_missing_headers_lowers_headers_score_but_not_others():
    score = calculate_score(GOOD_HTTPS, NO_HEADERS_PRESENT, NO_VERSION_LEAKS)

    assert score["headers_score"] == 0
    assert score["https_score"] == 40
    assert score["version_score"] == 25


def test_one_version_leak_costs_half_the_version_points():
    score = calculate_score(GOOD_HTTPS, ALL_HEADERS_PRESENT, ONE_VERSION_LEAK)

    # 2 tracked headers, 1 leaked -> half the 25 points, i.e. round(12.5).
    # Python's round() uses "banker's rounding" (round half to even), so
    # round(12.5) is 12, not 13 like you might expect from school math.
    assert score["version_score"] == 12


def test_score_breakdown_adds_up_to_total():
    score = calculate_score(GOOD_HTTPS, NO_HEADERS_PRESENT, ONE_VERSION_LEAK)

    assert score["total"] == score["https_score"] + score["headers_score"] + score["version_score"]
