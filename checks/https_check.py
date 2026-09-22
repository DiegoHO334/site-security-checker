"""HTTPS and SSL certificate check."""

import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse


def check_https(url: str, timeout: float = 5.0) -> dict:
    """Check whether a URL uses HTTPS, and if so, whether its certificate
    is valid and how many days remain until it expires.

    Returns a dict describing the result. It never raises for expected
    network/SSL failures -- those are reported inside the dict instead,
    so the rest of the program can treat every check the same way.
    """
    parsed = urlparse(url)

    if parsed.scheme != "https":
        return {
            "url": url,
            "uses_https": False,
            "cert_valid": None,
            "days_until_expiry": None,
            "error": None,
        }

    hostname = parsed.hostname
    port = parsed.port or 443

    result = {
        "url": url,
        "uses_https": True,
        "cert_valid": None,
        "days_until_expiry": None,
        "error": None,
    }

    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
    except ssl.SSLCertVerificationError as exc:
        result["cert_valid"] = False
        result["error"] = f"certificate verification failed: {exc.verify_message}"
        return result
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as exc:
        result["cert_valid"] = None
        result["error"] = f"could not connect: {exc}"
        return result

    expires_at = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
    expires_at = expires_at.replace(tzinfo=timezone.utc)
    days_until_expiry = (expires_at - datetime.now(timezone.utc)).days

    result["cert_valid"] = True
    result["days_until_expiry"] = days_until_expiry
    return result
