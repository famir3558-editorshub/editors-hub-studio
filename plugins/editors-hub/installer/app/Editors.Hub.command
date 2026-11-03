#!/bin/bash
# Double-click on a Mac: starts Editors.Hub and opens Home in your browser.
cd "$(dirname "$0")"
python3 studio.py open --browser || { echo; echo "Editors.Hub needs Python 3: https://www.python.org/downloads/"; read -n1 -p "Press any key to close"; }
