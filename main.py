from report import generate_report, format_report


def main():
    url = input("Enter a URL to check (e.g. https://example.com): ").strip()
    report = generate_report(url)
    print()
    print(format_report(report))


if __name__ == "__main__":
    main()
