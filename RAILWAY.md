# HERITIA — Railway (2 services)

Railpack ne peut pas builder la racine (`backend/` + `frontend/`).  
Déployer **deux services** depuis `cyrilalepsa/heritia` :

| Service | Root Directory | Start |
|---------|----------------|--------|
| `heritia-api` | `backend` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| `heritia-web` | `frontend` | `npx serve -s dist -l $PORT` |

## Variables

**heritia-api**
- `HERITIA_ENVIRONMENT=production`
- `HERITIA_APP_BASE_URL=https://heritia.neriacorp.com`
- `HERITIA_FRONTEND_URL=https://heritia.neriacorp.com`
- `HERITIA_SECRET_KEY=...`
- `HERITIA_STRIPE_SECRET_KEY=...`
- `HERITIA_CORS_ORIGINS=["https://heritia.neriacorp.com"]`

**heritia-web** (build-time Vite)
- `VITE_API_URL=https://<heritia-api-public-url>/api`
- `VITE_APP_URL=https://heritia.neriacorp.com`
