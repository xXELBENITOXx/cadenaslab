#!/bin/sh
cd "$(dirname "$0")"
printf 'Abre http://localhost:8765 en tu navegador.\n'
python3 src/local_server.py
