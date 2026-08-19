#!/usr/bin/env bash
# Baixa o modelo GGUF (Q4_K_M, ~3B) usado pelo NormaExtractor.
# Uso: ./scripts/download_model.sh [diretorio_destino]
set -euo pipefail

DEST_DIR="${1:-./models}"
MODEL_REPO="bartowski/Qwen2.5-3B-Instruct-GGUF"
MODEL_FILE="Qwen2.5-3B-Instruct-Q4_K_M.gguf"
URL="https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}"

mkdir -p "${DEST_DIR}"
echo "Baixando ${MODEL_FILE} (~1.9 GB) para ${DEST_DIR} ..."
curl -fL --progress-bar -o "${DEST_DIR}/${MODEL_FILE}" "${URL}"
echo "Concluído: ${DEST_DIR}/${MODEL_FILE}"
echo "Configure MODEL_PATH=${DEST_DIR}/${MODEL_FILE} no .env"
