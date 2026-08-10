# HERITIA — Railway (2 services)

Cause de l’erreur Railpack initiale : un seul service à la racine (`backend/` + `frontend/`) ne peut pas être détecté.

## Services (projet `lovely-expression`)

| Service | Root Directory | URL |
|---------|----------------|-----|
| `heritia-api` | `backend` | https://heritia-api-production.up.railway.app |
| `heritia-web` | `frontend` | https://heritia-web-production.up.railway.app |

Repo GitHub : https://github.com/cyrilalepsa/heritia

### heritia-api
- Start : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health : `/api/health`
- Vars : `HERITIA_ENVIRONMENT=production`, `HERITIA_APP_BASE_URL`, `HERITIA_FRONTEND_URL`, `HERITIA_SECRET_KEY`, …

### heritia-web
- Build : `frontend/Dockerfile`
- Start : `node server.mjs`
- Vars build : `VITE_API_URL=https://heritia-api-production.up.railway.app/api`, `VITE_APP_URL=https://heritia.neriacorp.com`
- Runtime : aligner `PORT` et le **target port** du domaine (ex. `3000`)

### Domaine custom
Brancher `heritia.neriacorp.com` sur `heritia-web`, et éventuellement `api.heritia…` sur `heritia-api`.