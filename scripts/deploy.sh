#!/usr/bin/env bash
# Executado NO SERVIDOR (via SSH pelo CI/CD ou manualmente).
# Faz pull da main, rebuilda e reinicia o app.
set -euo pipefail

APP_DIR="${APP_DIR:-/home/rafael/normaextractor}"
cd "${APP_DIR}"

git fetch origin main
git reset --hard origin/main

docker compose build
docker compose up -d

echo "Deploy concluído: $(docker ps --filter name=normaextractor-app --format '{{.Status}}')"
