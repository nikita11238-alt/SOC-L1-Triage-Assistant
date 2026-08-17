#!/usr/bin/env bash
# SOC L1 Triage Assistant — run.sh

cd "$(dirname "$0")/.." || exit 1

echo "==============================="
echo "    SOC L1 Triage Assistant"
echo "==============================="
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[-] python3 not found. Install Python 3 and try again."
    exit 1
fi

# Warn if output already exists (do not overwrite silently)
if [ -f "output/final_report.txt" ]; then
    echo "[!] Previous report exists — it will be saved to output/archive/"
    echo ""
fi

echo "[*] 1/4 Parsing logs..."
python3 scripts/triage.py || { echo "[-] triage.py failed. Check logs in the logs/ folder"; exit 1; }

echo ""
echo "[*] 2/4 Scoring severity..."
python3 scripts/severity.py || { echo "[-] severity.py failed."; exit 1; }

echo ""
echo "[*] 3/4 Generating report..."
python3 scripts/report.py || { echo "[-] report.py failed."; exit 1; }

echo ""
echo "[*] 4/4 Adding assessment..."
python3 scripts/ai_explainer.py || { echo "[-] ai_explainer.py failed."; exit 1; }

echo ""
echo "==============================="
echo "[✓] DONE"
echo "    Report: output/final_report.txt"
echo "    IOCs:   output/iocs.txt"
echo "    Top:    output/event_counts.txt"
echo "==============================="
