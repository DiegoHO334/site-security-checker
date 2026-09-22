"""Security headers check."""

import requests

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def check_headers(url: str, timeout: float = 5.0) -> dict:
    """Check which of the core security headers a site sends.

    Returns a dict with the value seen for each header (None if missing)
    and a list of the ones that were missing. Like check_https, network
    failures are reported inside the dict rather than raised.
    """
    result = {
        "url": url,
        "headers": {name: None for name in SECURITY_HEADERS},
        "missing": [],
        "error": None,
    }

    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        result["error"] = f"could not fetch headers: {exc}"
        result["missing"] = list(SECURITY_HEADERS)
        return result

    for name in SECURITY_HEADERS:
        value = response.headers.get(name)
        result["headers"][name] = value
        if value is None:
            result["missing"].append(name)

    return result
