#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi
python3 -m pip install -r requirements.txt
python3 main.py
echo ""
read -p "Press Enter to exit..."
