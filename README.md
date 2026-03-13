# SOC L1 Triage Assistant
A lightweight tool for rapid log analysis and incident triage report generation.

## Requirements
- Python 3.x (check: `python3 --version`)

## Quick Start
1. Copy the `SOC_L1_Triage_Assistant/` folder wherever you want
2. Place your log files into the `logs/` folder
3. Run:

```bash
chmod +x scripts/run.sh   # once
./scripts/run.sh
```

**Windows:**
```
scripts\run.bat
```

4. Check the result in `output/final_report.txt`

## Structure
```
SOC_L1_Triage_Assistant/
├── logs/           ← place your .log files here
├── output/         ← analysis results
│   ├── events.txt       — suspicious lines found
│   ├── event_counts.txt — top repeated events
│   ├── iocs.txt         — IPs and usernames
│   ├── severity.txt     — threat level (LOW/MEDIUM/HIGH)
│   └── final_report.txt — final SOC report
└── scripts/        ← do not modify
```

## What it detects

| Keyword | Meaning |
|---------|---------|
| failed | Failed login attempt |
| invalid | Invalid username or password |
| unauthorized | Access not permitted |
| sudo / root | Privilege escalation attempt |
| denied | Access denied |

## Severity levels

| Level | Score | Action |
|-------|-------|--------|
| LOW | 0–3 | Monitor |
| MEDIUM | 4–7 | Investigate within a few hours |
| HIGH | 8+ | Escalate immediately |

## MITRE ATT&CK
- T1110 — Brute Force
- T1078 — Valid Accounts
- T1021 — Remote Services

## Disclaimer
This tool is rule-based — not a SIEM replacement. Always review raw logs manually before taking action.

## License MIT
