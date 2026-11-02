# PentestAI — AI Agent for Automated Penetration Testing

A beginner-friendly hackathon starter for a **human-supervised, authorized security assessment workflow**.

## Current implementation

- Flask dashboard
- SQLite assessment history
- Loopback-only target validation (`localhost`, `127.0.0.1`, `::1`)
- Minimal, non-destructive HTTP GET request
- Basic HTTP security-header review
- Evidence, confidence, severity and defensive recommendations
- JSON report download

> **Important:** This is a starter prototype, not a full penetration-testing platform and not a substitute for professional security testing. The current checks are deliberately limited to local lab targets. Do not remove the scope controls or test systems without explicit written authorization.

## Requirements

- Python 3.10+
- pip

## Run on Windows 10

1. Extract or clone this repository.
2. Open Command Prompt in the project folder.
3. Create a virtual environment:

   ```bat
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bat
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## Run a local test target

In a second Command Prompt window, start a simple local HTTP server:

```bat
python -m http.server 8000 --bind 127.0.0.1
```

In PentestAI, enter:

```text
http://127.0.0.1:8000
```

The dashboard will run the limited header checks and show a report. Results are illustrative security observations and must be manually verified.

## Project structure

```text
PentestAI_GitHub_Repository/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── index.html
│   └── report.html
└── static/
    └── style.css
```

## Roadmap

- Add user authentication and role-based access
- Add explicit written-authorization records and scope expiry
- Add structured audit logging
- Add safe integration with a local training lab scanner
- Add evidence-backed AI summaries with human approval
- Add PDF report export and automated tests

## Safety

This repository is designed for localhost training only. It does not include exploit execution, credential attacks, stealth, persistence, destructive tests, or arbitrary public-target scanning.
