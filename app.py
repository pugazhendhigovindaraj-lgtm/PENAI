from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from urllib.parse import urlparse
from datetime import datetime, timezone
import sqlite3, json, io, os, requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deployment")
DB = os.environ.get("PENTESTAI_DB", "pentestai.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL, created_at TEXT NOT NULL,
            status TEXT NOT NULL, findings TEXT NOT NULL)""")

def validate_target(target):
    """Intentionally restrict this starter to loopback lab targets only."""
    try:
        p = urlparse(target)
        host = (p.hostname or "").lower()
        if p.scheme not in ("http", "https") or not host:
            return False, "Enter a valid http:// or https:// URL."
        allowed = host in ("localhost", "127.0.0.1", "::1")
        if not allowed:
            return False, "This starter permits loopback lab targets only (localhost / 127.0.0.1 / ::1)."
        return True, ""
    except Exception:
        return False, "Invalid target URL."

def inspect_headers(target):
    findings = []
    try:
        # Deliberately minimal, non-destructive GET request to local lab only.
        response = requests.get(target, timeout=5, allow_redirects=False,
                                headers={"User-Agent": "PentestAI-Lab/1.0"})
        headers = {k.lower(): v for k, v in response.headers.items()}
        checks = [
            ("Content-Security-Policy", "content-security-policy", "MEDIUM",
             "Consider a restrictive Content-Security-Policy to reduce the impact of content injection."),
            ("X-Content-Type-Options", "x-content-type-options", "LOW",
             "Set X-Content-Type-Options: nosniff to reduce MIME-sniffing risks."),
            ("X-Frame-Options", "x-frame-options", "LOW",
             "Use an appropriate frame policy (or CSP frame-ancestors) to reduce clickjacking risk."),
            ("Strict-Transport-Security", "strict-transport-security", "INFO",
             "For HTTPS deployments, consider an appropriate HSTS policy.")
        ]
        for label, key, severity, advice in checks:
            if key not in headers:
                findings.append({
                    "title": f"Missing {label} header",
                    "severity": severity,
                    "confidence": "High",
                    "evidence": f"The response did not include the {label} header.",
                    "recommendation": advice
                })
        findings.append({
            "title": "HTTP response received",
            "severity": "INFO",
            "confidence": "High",
            "evidence": f"Local lab responded with HTTP {response.status_code}.",
            "recommendation": "Review the response and confirm that the application behavior is expected."
        })
    except requests.RequestException as exc:
        findings.append({
            "title": "Target could not be reached",
            "severity": "INFO",
            "confidence": "High",
            "evidence": str(exc)[:250],
            "recommendation": "Start your local lab server and verify the URL and port."
        })
    return findings

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        ok, message = validate_target(target)
        if not ok:
            flash(message, "error")
            return redirect(url_for("index"))
        findings = inspect_headers(target)
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with db() as con:
            cur = con.execute(
                "INSERT INTO assessments(target, created_at, status, findings) VALUES(?,?,?,?)",
                (target, created, "Completed", json.dumps(findings)))
            assessment_id = cur.lastrowid
        return redirect(url_for("report", assessment_id=assessment_id))
    with db() as con:
        recent = con.execute("SELECT id,target,created_at,status FROM assessments ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("index.html", recent=recent)

@app.route("/report/<int:assessment_id>")
def report(assessment_id):
    with db() as con:
        row = con.execute("SELECT * FROM assessments WHERE id=?", (assessment_id,)).fetchone()
    if not row:
        flash("Assessment not found.", "error")
        return redirect(url_for("index"))
    return render_template("report.html", item=row, findings=json.loads(row["findings"]))

@app.route("/report/<int:assessment_id>/download")
def download_report(assessment_id):
    with db() as con:
        row = con.execute("SELECT * FROM assessments WHERE id=?", (assessment_id,)).fetchone()
    if not row:
        return "Not found", 404
    payload = {
        "project": "PentestAI",
        "assessment_id": row["id"],
        "target": row["target"],
        "created_at": row["created_at"],
        "status": row["status"],
        "findings": json.loads(row["findings"]),
        "note": "Starter lab report. Findings require human verification."
    }
    stream = io.BytesIO(json.dumps(payload, indent=2).encode("utf-8"))
    return send_file(stream, mimetype="application/json", as_attachment=True,
                     download_name=f"pentestai-report-{assessment_id}.json")

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
