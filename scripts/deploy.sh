#!/usr/bin/env bash
# Executado NO SERVIDOR (via SSH pelo CI/CD ou manualmente).
# Atualiza o código e INICIA o build em segundo plano, desacoplado do SSH.
# Isso evita que a compilação pesada derrube a sessão SSH (broken pipe).
set -euo pipefail

APP_DIR="${APP_DIR:-/home/rafael/normaextractor}"
cd "${APP_DIR}"

git fetch origin main
git reset --hard origin/main

rm -f build.log
nohup docker compose build </dev/null > build.log 2>&1 &
echo "Build iniciado em segundo plano (PID $!)"
