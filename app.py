"""Flask web front end for the site security checker.

Deliberately thin: all the actual work (running checks, scoring) lives
in report.py and checks/, which main.py (the CLI) also uses. This file
only handles turning a browser request into a call to generate_report()
and turning the result into HTML.
"""

from flask import Flask, render_template, request

from report import generate_report

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            error = "Please enter a URL."
        else:
            report = generate_report(url)

    return render_template("index.html", report=report, error=error)


if __name__ == "__main__":
    app.run(debug=True)
