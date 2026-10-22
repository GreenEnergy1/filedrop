#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
if [ ! -f settings.json ]; then python setup.py; fi
python app.py
