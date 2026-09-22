from checks.https_check import check_https
from checks.headers_check import check_headers


def main():
    url = input("Enter a URL to check (e.g. https://example.com): ").strip()

    https_result = check_https(url)
    print()
    print(f"URL:              {https_result['url']}")
    print(f"Uses HTTPS:       {https_result['uses_https']}")
    print(f"Certificate valid:{https_result['cert_valid']}")
    print(f"Days until expiry:{https_result['days_until_expiry']}")
    if https_result["error"]:
        print(f"Error:            {https_result['error']}")

    headers_result = check_headers(url)
    print()
    print("Security headers:")
    for name, value in headers_result["headers"].items():
        print(f"  {name}: {value if value is not None else 'MISSING'}")
    if headers_result["error"]:
        print(f"Error: {headers_result['error']}")


if __name__ == "__main__":
    main()
