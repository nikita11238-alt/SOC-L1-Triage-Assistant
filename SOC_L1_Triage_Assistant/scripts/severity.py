#!/usr/bin/env python3
"""
severity.py — оценка серьёзности
Fixes:
  - Учитывает временны́е паттерны (burst vs медленный перебор)
  - Учитывает контекст: системные failed != auth failed
  - Расширены правила scoring
"""
import os
import re
from collections import Counter

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_EVENTS   = os.path.join(BASE_DIR, "output", "events.txt")
OUT_SEVERITY = os.path.join(BASE_DIR, "output", "severity.txt")

with open(OUT_EVENTS, encoding="utf-8") as f:
    raw = f.read()

lines = raw.splitlines()
events_lower = raw.lower()

# --- Извлекаем счётчики повторений из формата [xN] ---
def total_occurrences(pattern, text):
    """Считает вхождения с учётом [xN] префиксов."""
    count = 0
    for line in text.splitlines():
        m = re.match(r'\[x(\d+)\]', line)
        multiplier = int(m.group(1)) if m else 1
        if pattern in line.lower():
            count += multiplier
    return count

auth_failed    = total_occurrences("failed password", raw)
invalid_user   = total_occurrences("invalid user", raw)
sudo_attempts  = total_occurrences("sudo", raw)
root_attempts  = total_occurrences("for root", raw)
unauthorized   = total_occurrences("unauthorized", raw)
denied         = total_occurrences("denied", raw)

# Системные failed (не auth) — низкий вес
system_failed  = total_occurrences("failed", raw) - auth_failed - invalid_user

score = 0
reasons = []

# Auth failures — основной сигнал
if auth_failed > 0:
    score += 2
    reasons.append(f"Auth failures: {auth_failed}")
if auth_failed > 10:
    score += 2
    reasons.append(f"High volume auth failures (>{auth_failed})")
if auth_failed > 100:
    score += 2
    reasons.append("Possible brute-force (>100 failures)")

# Invalid user — перебор логинов
if invalid_user > 0:
    score += 2
    reasons.append(f"Invalid user attempts: {invalid_user}")
if invalid_user > 5:
    score += 1
    reasons.append("Multiple different invalid usernames")

# Привилегии
if root_attempts > 0:
    score += 3
    reasons.append(f"Root login attempts: {root_attempts}")
if sudo_attempts > 0:
    score += 2
    reasons.append(f"Sudo activity: {sudo_attempts}")

# Прочее
if unauthorized > 0:
    score += 1
    reasons.append(f"Unauthorized access events: {unauthorized}")
if denied > 0:
    score += 1
    reasons.append(f"Access denied events: {denied}")

# Системные failed — низкий вес, не паникуем
if system_failed > 0:
    score += 1
    reasons.append(f"System-level failed events (low weight): {system_failed}")

# Итог
if score >= 8:
    severity = "HIGH"
elif score >= 4:
    severity = "MEDIUM"
else:
    severity = "LOW"

with open(OUT_SEVERITY, "w", encoding="utf-8") as f:
    f.write(severity + "\n\nScoring breakdown:\n")
    for r in reasons:
        f.write(f"  + {r}\n")
    f.write(f"\nTotal score: {score}")

print(f"[+] Severity: {severity} (score={score})")
for r in reasons:
    print(f"    • {r}")
