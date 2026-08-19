# NormaExtractor

Sistema para ingestão de documentos normativos (PDF/DOCX/TXT), extração estruturada de cláusulas (tipo, sujeito, ação, prazo, base legal, penalidade) com SLM local, indexação semântica e consulta interativa via chat (RAG) com streaming.

- **Backend:** FastAPI + SQLite (SQLAlchemy/Alembic) + ChromaDB embedded + sentence-transformers (all-MiniLM-L6-v2) + llama-cpp-python (GGUF Q4_K_M em CPU)
- **Frontend:** React 18 + TypeScript + Vite (SPA servida pelo próprio backend)
- **Deploy:** Docker (imagem única) + docker-compose, atrás do nginx central da VPS
- **Produção:** https://normaextractor.adolfo.tec.br

Os requisitos completos estão em `docs/` (SRS + fichas REQ-*).

## Estrutura

```
backend/     # API FastAPI, pipeline de processamento, RAG, auth JWT
frontend/    # SPA React (login, upload, dashboard, chat SSE)
nginx/       # server block do domínio (montado no nginx central da VPS)
scripts/     # download_model.sh, deploy.sh
docs/        # SRS e requisitos
```

## Rodar localmente (desenvolvimento)

Pré-requisitos: Python 3.10+, Node 20+, ~2 GB livres de RAM para o modelo.

```bash
# 1. Modelo GGUF (uma única vez, ~1.9 GB)
./scripts/download_model.sh

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajuste JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD, MODEL_PATH
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend (outro terminal)
cd frontend
npm install
npm run dev            # http://localhost:5173 com proxy para :8000
```

Testes do backend: `cd backend && python -m pytest tests/`.

## Deploy (VPS)

O deploy é automático via GitHub Actions em todo push na `main` (workflow
`CI/CD`, job `deploy` → SSH → `scripts/deploy.sh` no servidor). Pré-requisitos
no servidor (`/home/rafael/normaextractor`):

1. Clone do repositório e `.env` preenchido (ver `.env.example`).
2. Modelo GGUF em `models/` (`./scripts/download_model.sh`).
3. Certificado Let's Encrypt para `normaextractor.adolfo.tec.br` (certbot
   webroot em `/home/rafael/quest/certbot`).
4. `nginx/normaextractor.adolfo.tec.br.conf` montado no container
   `questtrainer-nginx` (nginx central) + reload.

Manual:

```bash
ssh rafael@187.77.247.25
cd /home/rafael/normaextractor
docker compose build && docker compose up -d
```

## API (resumo)

| Rota | Auth | Descrição |
|------|------|-----------|
| `POST /api/v1/auth/login` | não | login email+senha → JWT (24h) |
| `GET /api/v1/health` | não | healthcheck |
| `POST /api/v1/documents/upload` | sim | upload PDF/DOCX/TXT (1 KB–20 MB) |
| `GET /api/v1/documents` | sim | lista com filtros (status, tipo, período) |
| `GET /api/v1/documents/{id}` | sim | detalhe do documento |
| `DELETE /api/v1/documents/{id}` | sim | exclui documento (cascata) |
| `GET /api/v1/documents/{id}/extractions` | sim | extrações estruturadas |
| `POST /api/v1/chat` | sim | RAG com streaming SSE (token/sources/done) |
| `GET /api/v1/metrics` | sim | coverage, consistência, latência média |

Documentação interativa (OpenAPI): `/docs`.
