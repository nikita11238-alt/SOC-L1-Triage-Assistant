# SOC L1 Triage Assistant

A lightweight, offline Python tool that automates first-level incident triage — parsing logs, extracting IOCs, scoring severity, and generating structured SOC reports.

Built as a learning project while studying for a SOC analyst role.

---

## What it does

1. **Parses logs** — scans for suspicious keywords: `failed`, `invalid`, `unauthorized`, `sudo`, `root`, `denied`
2. **Extracts IOCs** — validates and collects IP addresses and usernames
3. **Deduplicates events** — counts repetitions to detect brute-force patterns
4. **Scores severity** — LOW / MEDIUM / HIGH with full scoring breakdown
5. **Generates a report** — structured SOC-style output mapped to MITRE ATT&CK

---

## Example output

```
============================================================
         SOC INCIDENT TRIAGE REPORT
============================================================
Date     : 2026-03-13 14:57:37
Severity : HIGH

INDICATORS OF COMPROMISE
IPs:
185.220.101.45
92.118.160.12
45.33.32.156

Users:
admin, root, john, alice

SEVERITY SCORING
  + Auth failures: 22
  + High volume auth failures (>22)
  + Root login attempts: 6
  + Sudo activity: 3
Total score: 14

MITRE ATT&CK:
  T1110 — Brute Force
  T1078 — Valid Accounts
  T1021 — Remote Services
```

---

## Requirements

- Python 3.x
- No external dependencies

---

## Usage

### Windows
```
scripts\run.bat
```
Double-click `run.bat` — it auto-detects Python, runs the pipeline, and opens the report in Notepad.

### Linux / macOS
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

---

## Project structure

```
SOC_L1_Triage_Assistant/
├── logs/                  ← place your log files here
├── output/
│   ├── events.txt         — deduplicated suspicious events
│   ├── event_counts.txt   — top repeated events
│   ├── iocs.txt           — extracted IPs and usernames
│   ├── severity.txt       — severity level + scoring breakdown
│   ├── final_report.txt   — full SOC report
│   └── archive/           — previous reports (auto-saved)
└── scripts/
    ├── triage.py          — log parsing, IOC extraction
    ├── severity.py        — severity scoring
    ├── report.py          — report generation
    ├── ai_explainer.py    — rule-based assessment
    ├── run.sh             — Linux/macOS launcher
    └── run.bat            — Windows launcher
```

---

## Severity scoring

| Signal | Points |
|--------|--------|
| Auth failures present | +2 |
| Auth failures > 10 | +2 |
| Auth failures > 100 | +2 |
| Invalid usernames | +2 |
| Multiple different invalid users | +1 |
| Root login attempts | +3 |
| Sudo activity | +2 |
| Unauthorized events | +1 |
| Access denied events | +1 |

| Score | Severity |
|-------|----------|
| 0–3 | LOW |
| 4–7 | MEDIUM |
| 8+ | HIGH |

---

## Limitations

This is a keyword-based rule engine — not a SIEM replacement.

- **False positives**: system events containing "failed" may trigger alerts
- **False negatives**: attacks not involving these keywords won't be caught
- **No timeline analysis**: 100 failures in 1 second vs 1 month look the same
- **The "AI Assessment" is rule-based** — three pre-written phrases, not actual AI

Use this as a first-pass filter, then review raw logs manually.

---

## MITRE ATT&CK coverage

| Technique | ID | Description |
|-----------|-----|-------------|
| Brute Force | T1110 | Password spraying / credential stuffing |
| Valid Accounts | T1078 | Use of legitimate credentials |
| Remote Services | T1021 | SSH-based lateral movement |

---

## What I learned

- How brute-force patterns appear in raw SSH logs
- Why context matters: `systemd: job failed` ≠ `sshd: Failed password`
- MITRE ATT&CK mapping in practice
- Limits of keyword-based detection vs. behavioral analysis

---

*Built by Mykyta Morar — learning cybersecurity one project at a time.*
