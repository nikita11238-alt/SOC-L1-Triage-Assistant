#!/usr/bin/env python3
"""
ai_explainer.py
Fixes:
  - Честный дисклеймер: это НЕ AI, это правила
  - Не дописывает дважды при повторном запуске (перезаписывает секцию)
  - Расширенные объяснения по уровням
"""
import os
import re

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SEVERITY = os.path.join(BASE_DIR, "output", "severity.txt")
OUT_REPORT   = os.path.join(BASE_DIR, "output", "final_report.txt")

with open(OUT_SEVERITY, encoding="utf-8") as f:
    severity = f.readline().strip()

assessments = {
    "HIGH": (
        "RULE-BASED ASSESSMENT (not AI):\n"
        "Multiple high-confidence indicators detected:\n"
        "  • High volume of authentication failures suggests brute-force\n"
        "  • Root/sudo activity may indicate privilege escalation attempt\n"
        "  • Invalid usernames suggest credential stuffing or enumeration\n"
        "\n"
        "ACTION REQUIRED: Escalate immediately. Do not rely solely on this\n"
        "report — review raw logs manually before taking blocking action."
    ),
    "MEDIUM": (
        "RULE-BASED ASSESSMENT (not AI):\n"
        "Moderate indicators detected. Could be legitimate activity or early\n"
        "stage of an attack:\n"
        "  • Some authentication failures observed\n"
        "  • Requires analyst review within a few hours\n"
        "\n"
        "ACTION REQUIRED: Investigate source IPs and affected accounts.\n"
        "Check if activity correlates with known admin work or tests."
    ),
    "LOW": (
        "RULE-BASED ASSESSMENT (not AI):\n"
        "Low-level suspicious keywords found. Likely routine noise:\n"
        "  • Small number of failures — may be normal user mistakes\n"
        "  • No strong indicators of active attack\n"
        "\n"
        "ACTION REQUIRED: Document and monitor. Re-run analysis if volume\n"
        "increases. Check again in 24h."
    ),
}

text = assessments.get(severity, f"Unknown severity level: {severity}")

# Читаем отчёт и заменяем секцию если она уже есть (не дублируем)
with open(OUT_REPORT, "r", encoding="utf-8") as f:
    report = f.read()

SECTION_MARKER = "\n=== AUTOMATED ASSESSMENT ===\n"

# Убираем старую секцию если есть
if SECTION_MARKER in report:
    report = report[:report.index(SECTION_MARKER)]

report += SECTION_MARKER + text + "\n"

with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write(report)

print("[+] Assessment added (rule-based, not AI)")
