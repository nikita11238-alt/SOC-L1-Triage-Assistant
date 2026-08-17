#!/usr/bin/env python3
"""
severity.py — severity assessment
Updates:
  - Single-pass line processing (accurate counts without overlapping subtraction bugs)
  - Fixed threshold reporting strings
  - Clean and robust event categorization
"""
import os
import re

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_EVENTS   = os.path.join(BASE_DIR, "output", "events.txt")
OUT_SEVERITY = os.path.join(BASE_DIR, "output", "severity.txt")

with open(OUT_EVENTS, encoding="utf-8") as f:
    raw = f.read()

auth_failed   = 0
invalid_user  = 0
sudo_attempts = 0
root_attempts = 0
unauthorized  = 0
denied        = 0
system_failed = 0

# --- Single pass parsing to avoid overlapping subtraction bugs ---
for line in raw.splitlines():
    m = re.match(r'\[x(\d+)\]\s*(.*)', line)
    if m:
        count = int(m.group(1))
        content = m.group(2).lower()
    else:
        count = 1
        content = line.lower()

    is_auth = "failed password" in content
    is_inv  = "invalid user" in content

    if is_auth:
        auth_failed += count
    if is_inv:
        invalid_user += count
    
    # System-level failed (contains 'failed' but is not an auth password failure)
    if "failed" in content and not is_auth:
        system_failed += count

    if "sudo" in content:
        sudo_attempts += count
    if "for root" in content:
        root_attempts += count
    if "unauthorized" in content:
        unauthorized += count
    if "denied" in content:
        denied += count

score = 0
reasons = []

# Auth failures — main signal
if auth_failed > 0:
    score += 2
    reasons.append(f"Auth failures: {auth_failed}")
if auth_failed > 10:
    score += 2
    reasons.append("High volume auth failures (>10)")
if auth_failed > 100:
    score += 2
    reasons.append("Possible brute-force (>100 failures)")

# Invalid user — login enumeration
if invalid_user > 0:
    score += 2
    reasons.append(f"Invalid user attempts: {invalid_user}")
if invalid_user > 5:
    score += 1
    reasons.append("Multiple different invalid usernames (>5)")

# Privileges
if root_attempts > 0:
    score += 3
    reasons.append(f"Root login attempts: {root_attempts}")
if sudo_attempts > 0:
    score += 2
    reasons.append(f"Sudo activity: {sudo_attempts}")

# Other
if unauthorized > 0:
    score += 1
    reasons.append(f"Unauthorized access events: {unauthorized}")
if denied > 0:
    score += 1
    reasons.append(f"Access denied events: {denied}")

# System-level failed — low weight, no panic
if system_failed > 0:
    score += 1
    reasons.append(f"System-level failed events (low weight): {system_failed}")

# Final result
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
