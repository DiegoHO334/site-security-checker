# Site Security Checker

A Python command-line tool that checks a website's HTTPS/certificate setup,
security headers, and whether it leaks server software versions, then
outputs a report with an overall score.

## Status

HTTPS/certificate check (`checks/https_check.py`) and security headers
check (`checks/headers_check.py`) exist, both wired up in `main.py`.
Version-leak check, scoring, and report output are NOT built yet — do
not assume they exist.

## User background

- Computer science major, cybersecurity track.
- Beginner at coding overall; has some Java experience but is new to Python.
- Wants to actually understand every piece of code written, not just receive
  a finished script. Explain concepts as they come up, especially anything
  Python-specific (vs. Java) or networking-related (sockets, TLS/SSL, DNS),
  since this project ties directly into their coursework.

## Working style

- Build incrementally, one piece at a time. Don't jump ahead to future
  checks/features unless asked.
- Prefer plain, well-explained code over clever/compressed code.
- Comments in this codebase may be a bit more explanatory than usual given
  it's a learning project, but should still focus on the WHY / non-obvious
  parts (e.g. why we catch a specific exception) rather than narrating the
  obvious.
