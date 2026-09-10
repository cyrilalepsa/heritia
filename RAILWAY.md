# HERITIA — Railway (2 services) + Single Ingress N2

Cause de l'erreur Railpack initiale : un seul service à la racine (`backend/` + `frontend/`) ne peut pas être détecté.

## Architecture production

```text
heritia.neriacorp.com
        │
        ▼
Single Ingress N2 (infra/n2/)
   ├── /api/*  → heritia-api (Railway)
   └── /*      → heritia-web  (Railway SPA)
```

Le frontend utilise **`VITE_API_URL=/api`** (same-origin via N2). Voir `infra/n2/DEPLOY-N2.md` pour la checklist manuelle DNS / Cloudflare / N2.

## Services (projet `lovely-expression`)

| Service | Root Directory | URL interne Railway |
|---------|----------------|---------------------|
| `heritia-api` | `backend` | https://heritia-api-production.up.railway.app |
| `heritia-web` | `frontend` | https://heritia-web-production.up.railway.app |

Repo GitHub : https://github.com/cyrilalepsa/heritia

### heritia-api
- Start : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health : `/api/health`
- Vars : `HERITIA_ENVIRONMENT=production`, `HERITIA_APP_BASE_URL=https://heritia.neriacorp.com`, `N2_MASTER_KEY`, `RESEND_API_KEY`, …
- **Ne pas** exposer le domaine public directement si N2 proxy `/api`.

### heritia-web
- Build : `frontend/Dockerfile`
- Start : `node server.mjs`
- Vars build : `VITE_API_URL=/api`, `VITE_APP_URL=https://heritia.neriacorp.com`
- Runtime : aligner `PORT` et le **target port** (ex. `3000`)
- **Ne pas** attacher `heritia.neriacorp.com` en domaine custom Railway si le trafic passe par N2.

### Domaine custom (CRITIQUE)
`heritia.neriacorp.com` doit être routé par le **Single Ingress N2** vers `heritia-web` + `/api` → `heritia-api`, **pas** vers le shell PWA N2 Core par défaut.

Fichiers de câblage : `infra/n2/heritia.tenant.json`, `infra/n2/heritia.ingress.conf`.

Vérification après déploiement :
```bash
curl -sI https://heritia.neriacorp.com/health
# Attendu : X-Heritia-App: 1

curl -s https://heritia.neriacorp.com/health
# Attendu : {"status":"ok","app":"HERITIA"}

curl -s https://heritia.neriacorp.com/api/health
# Attendu : {"status":"ok","app":"HERITIA"}  (PAS n2-core)
```

Si vous voyez « Propulsé par NeriaCorp » ou le titre « NeriaCorp · N2 Core », la route tenant Heritia n'est pas active dans N2 — voir `infra/n2/DEPLOY-N2.md`.
