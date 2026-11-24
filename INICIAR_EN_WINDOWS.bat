@echo off
title CadenasLab - Servidor Python
cd /d "%~dp0"
start "" http://localhost:8765
python src\local_server.py
pause
