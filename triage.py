#!/usr/bin/env python3
"""
triage.py — парсинг логов
Fixes:
  - Стриминг построчно (не грузит весь файл в RAM)
  - Валидация IP (отсекает 999.x.x.x и т.п.)
  - Дедупликация событий (одинаковые строки считаются, не дублируются)
  - Кодировка: пробует UTF-8, fallback на latin-1
  - Счётчик повторений для каждого события
"""
import os
import re
import ipaddress
from collections import Counter

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FOLDER  = os.path.join(BASE_DIR, "logs")
OUT_EVENTS  = os.path.join(BASE_DIR, "output", "events.txt")
OUT_IOC     = os.path.join(BASE_DIR, "output", "iocs.txt")
OUT_COUNTS  = os.path.join(BASE_DIR, "output", "event_counts.txt")

KEYWORDS     = ["failed", "invalid", "unauthorized", "sudo", "root", "denied"]
IP_PATTERN   = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
USER_PATTERN = re.compile(r'user[=:\s]+(\w+)', re.I)

def is_valid_ip(ip_str):
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ValueError:
        return False

def open_log(path):
    """UTF-8 сначала, при ошибке latin-1."""
    try:
        f = open(path, encoding="utf-8")
        f.read(1024)
        f.seek(0)
        return f
    except UnicodeDecodeError:
        return open(path, encoding="latin-1")

os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)

log_files = [
    fn for fn in os.listdir(LOG_FOLDER)
    if os.path.isfile(os.path.join(LOG_FOLDER, fn)) and not fn.startswith(".")
]

if not log_files:
    print("[-] Папка logs/ пустая — положи туда лог-файлы и запусти снова.")
    exit(1)

event_counter = Counter()
ips   = set()
users = set()
total_lines = 0

for filename in log_files:
    path = os.path.join(LOG_FOLDER, filename)
    print(f"    Читаю: {filename}")
    try:
        with open_log(path) as f:
            for line in f:                   # построчно — RAM не растёт
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
        print(f"    [!] Не могу прочитать {filename}: {e}")

unique_events = len(event_counter)
total_events  = sum(event_counter.values())

# events.txt — уникальные строки + счётчик повторений
with open(OUT_EVENTS, "w", encoding="utf-8") as f:
    for line, count in event_counter.most_common():
        prefix = f"[x{count}] " if count > 1 else ""
        f.write(f"{prefix}{line}\n")

# iocs.txt
with open(OUT_IOC, "w", encoding="utf-8") as f:
    f.write("IPs:\n" + "\n".join(sorted(ips)))
    f.write("\n\nUsers:\n" + "\n".join(sorted(users)))

# event_counts.txt — топ-20 повторяющихся строк
with open(OUT_COUNTS, "w", encoding="utf-8") as f:
    f.write("Top repeated events:\n\n")
    for line, count in event_counter.most_common(20):
        f.write(f"{count:>6}x  {line[:120]}\n")

print(f"[+] Прочитано строк: {total_lines:,}")
print(f"[+] Уникальных событий: {unique_events:,} (всего вхождений: {total_events:,})")
print(f"[+] IPs: {len(ips)}, Users: {len(users)}")
