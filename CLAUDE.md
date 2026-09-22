# Site Security Checker

A Python command-line tool that checks a website's HTTPS/certificate setup,
security headers, and whether it leaks server software versions, then
outputs a report with an overall score.

## Status

HTTPS/certificate check (`checks/https_check.py`), security headers
check (`checks/headers_check.py`), server version leak check
(`checks/version_leak_check.py`), scoring (`checks/scoring.py`), and
a combined report (`report.py`, formats a 0-100 score + letter grade)
all exist. Two front ends both reuse report.py: the CLI (`main.py`)
and a Flask web app (`app.py`, `templates/index.html`,
`static/style.css`) with a URL form and styled results. Run the web
app with `python3 app.py` (dev server on http://127.0.0.1:5000).

Published to GitHub: https://github.com/DiegoHO334/site-security-checker

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
