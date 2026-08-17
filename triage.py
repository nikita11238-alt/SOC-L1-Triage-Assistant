#!/usr/bin/env python3
"""
triage.py — log parsing
Updates:
  - Line-by-line streaming (does not load the entire file into RAM)
  - IP validation (filters out invalid IPs like 999.x.x.x)
  - Event deduplication (identical lines are counted, not duplicated)
  - Encoding: tries UTF-8, falls back to latin-1 (with safe descriptor closing)
  - Occurrence counter for each event
"""
import os
import re
import ipaddress
from collections import Counter

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FOLDER   = os.path.join(BASE_DIR, "logs")
OUT_EVENTS   = os.path.join(BASE_DIR, "output", "events.txt")
OUT_IOC      = os.path.join(BASE_DIR, "output", "iocs.txt")
OUT_COUNTS   = os.path.join(BASE_DIR, "output", "event_counts.txt")

KEYWORDS     = ["failed", "invalid", "unauthorized", "sudo", "root", "denied"]
IP_PATTERN   = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
USER_PATTERN = re.compile(r'user[=:\s]+([\w\.-]+)', re.I)

def is_valid_ip(ip_str):
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ValueError:
        return False

def open_log(path):
    """Try UTF-8 first, fall back to latin-1 on error (with safe file closing)."""
    try:
        f = open(path, encoding="utf-8")
        f.read(1024)
        f.seek(0)
        return f
    except UnicodeDecodeError:
        if 'f' in locals() and not f.closed:
            f.close()
        return open(path, encoding="latin-1")

os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)

log_files = [
    fn for fn in os.listdir(LOG_FOLDER)
    if os.path.isfile(os.path.join(LOG_FOLDER, fn)) and not fn.startswith(".")
]

if not log_files:
    print("[-] logs/ folder is empty — put log files there and run again.")
    exit(1)

event_counter = Counter()
ips   = set()
users = set()
total_lines = 0

for filename in log_files:
    path = os.path.join(LOG_FOLDER, filename)
    print(f"    Reading: {filename}")
    try:
        with open_log(path) as f:
            for line in f:             # line-by-line — RAM footprint remains minimal
                total_lines += 1
                line = line.strip()
                if not line:
                    continue
                if any(k in line.lower() for k in KEYWORDS):
                    event_counter[line] += 1
                    for ip in IP_PATTERN.findall(line):
                        if is_valid_ip(ip):
                            ips.add(ip)
                    m = USER_PATTERN.search(line)
                    if m:
                        users.add(m.group(1))
    except OSError as e:
        print(f"    [!] Cannot read {filename}: {e}")

unique_events = len(event_counter)
total_events  = sum(event_counter.values())

# events.txt — unique lines + occurrence counter
with open(OUT_EVENTS, "w", encoding="utf-8") as f:
    for line, count in event_counter.most_common():
        prefix = f"[x{count}] " if count > 1 else ""
        f.write(f"{prefix}{line}\n")

# iocs.txt
with open(OUT_IOC, "w", encoding="utf-8") as f:
    f.write("IPs:\n" + "\n".join(sorted(ips)))
    f.write("\n\nUsers:\n" + "\n".join(sorted(users)))

# event_counts.txt — top 20 repeated lines
with open(OUT_COUNTS, "w", encoding="utf-8") as f:
    f.write("Top repeated events:\n\n")
    for line, count in event_counter.most_common(20):
        f.write(f"{count:>6}x  {line[:120]}\n")

print(f"[+] Lines read: {total_lines:,}")
print(f"[+] Unique events: {unique_events:,} (total occurrences: {total_events:,})")
print(f"[+] IPs: {len(ips)}, Users: {len(users)}")
