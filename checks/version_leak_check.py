"""Server software version leak check."""

import requests

# Headers servers sometimes use to advertise their software/version,
# e.g. "Server: nginx/1.18.0" or "X-Powered-By: PHP/8.1.2". That's
# useful info for an attacker looking for known vulnerabilities in a
# specific version, so a hardened site should avoid sending it.
VERSION_HEADERS = [
    "Server",
    "X-Powered-By",
]


def check_version_leak(url: str, timeout: float = 5.0) -> dict:
    """Check whether a site's response headers leak server software
    names/versions.

    Returns a dict with the raw value seen for each version-revealing
    header (None if absent) and a flag for whether the value looks
    specific enough to be a leak (e.g. "nginx/1.18.0") versus generic
    (e.g. just "nginx" with no version number).
    """
    result = {
        "url": url,
        "headers": {name: None for name in VERSION_HEADERS},
        "leaks": [],
        "error": None,
    }

    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        result["error"] = f"could not fetch headers: {exc}"
        return result

    for name in VERSION_HEADERS:
        value = response.headers.get(name)
        result["headers"][name] = value
        if value is not None and _looks_like_a_version(value):
            result["leaks"].append(name)

    return result


def _looks_like_a_version(value: str) -> bool:
    """True if the header value contains a digit, e.g. "nginx/1.18.0".

    A bare "nginx" or "Apache" names the software but not a specific
    version, so it's a smaller leak than "nginx/1.18.0" -- knowing the
    exact version lets an attacker look up known CVEs for it.
    """
    return any(char.isdigit() for char in value)
