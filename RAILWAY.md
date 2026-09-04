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
- Vars : `HERITIA_ENVIRONMENT=production`, `HERITIA_APP_BASE_URL`, `HERITIA_FRONTEND_URL`, `N2_MASTER_KEY`, `RESEND_API_KEY`, …

### heritia-web
- Build : `frontend/Dockerfile`
- Start : `node server.mjs`
- Vars build : `VITE_API_URL=https://heritia.neriacorp.com/api`, `VITE_APP_URL=https://heritia.neriacorp.com`
- Runtime : aligner `PORT` et le **target port** du domaine (ex. `3000`)

### Domaine custom (CRITIQUE)
`heritia.neriacorp.com` doit être attaché au service **`heritia-web`** (root `frontend`), **pas** au shell PWA NoyauNeria2.0.

Vérification après déploiement :
```bash
curl -sI https://heritia.neriacorp.com/health
# Attendu : X-Heritia-App: 1  et  {"status":"ok","app":"HERITIA"}
```

Si vous voyez « Propulsé par NeriaCorp » ou le logo Les Délices en Famille, le domaine pointe encore vers N2 — détachez-le du service N2 et rattachez-le à `heritia-web`.