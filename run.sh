#!/bin/bash
# SOC L1 Triage Assistant — run.sh

cd "$(dirname "$0")/.." || exit 1

echo "==============================="
echo "   SOC L1 Triage Assistant"
echo "==============================="
echo ""

# Проверяем Python3
if ! command -v python3 &> /dev/null; then
    echo "[-] python3 не найден. Установи Python 3 и повтори."
    exit 1
fi

# Предупреждение если output уже есть (не молча перезаписываем)
if [ -f "output/final_report.txt" ]; then
    echo "[!] Уже есть предыдущий отчёт — он будет сохранён в output/archive/"
    echo ""
fi

echo "[*] 1/4 Парсинг логов..."
python3 scripts/triage.py || { echo "[-] triage.py упал. Проверь логи в папке logs/"; exit 1; }

echo ""
echo "[*] 2/4 Оценка серьёзности..."
python3 scripts/severity.py || { echo "[-] severity.py упал."; exit 1; }

echo ""
echo "[*] 3/4 Генерация отчёта..."
python3 scripts/report.py || { echo "[-] report.py упал."; exit 1; }

echo ""
echo "[*] 4/4 Добавление оценки..."
python3 scripts/ai_explainer.py || { echo "[-] ai_explainer.py упал."; exit 1; }

echo ""
echo "==============================="
echo "[✓] ГОТОВО"
echo "    Смотри: output/final_report.txt"
echo "    IOCs:   output/iocs.txt"
echo "    Топ:    output/event_counts.txt"
echo "==============================="
