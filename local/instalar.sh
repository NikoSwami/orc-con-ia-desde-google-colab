#!/usr/bin/env bash
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$RAIZ/.venv"
REQ="requirements.txt"

if [ "${1:-}" = "--cpu" ]; then
    REQ="requirements-cpu.txt"
fi

if [ ! -d "$VENV" ]; then
    echo "Creando entorno virtual en $VENV"
    python3 -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip --quiet
"$VENV/bin/python" -m pip install --timeout 180 --retries 10 -r "$RAIZ/$REQ"

echo
echo "Listo. Para usarlo:"
echo "  source $VENV/bin/activate"
echo "  python ocr_local.py mis_pdfs/"
