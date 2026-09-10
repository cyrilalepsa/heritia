# HERITIA — déploiement via Single Ingress N2

Ce dossier décrit le câblage de `heritia.neriacorp.com` sur le **Single Ingress N2** (NoyauNeria2.0), avec proxy same-origin `/api` vers le backend Railway.

## Architecture cible

```text
Client
  │
  ▼
Cloudflare DNS (heritia.neriacorp.com)
  │
  ▼
Single Ingress N2 (TLS terminé ici)
  ├── /api/*  ──► heritia-api (Railway)
  └── /*      ──► heritia-web (Railway SPA)
```

Le frontend Heritia appelle **`/api`** (URL relative). Le proxy N2 route vers `heritia-api-production.up.railway.app`.

## Fichiers de ce dossier

| Fichier | Rôle |
|---------|------|
| `heritia.tenant.json` | Registre tenant N2 (priorité, routes, healthchecks) |
| `heritia.ingress.conf` | Snippet nginx à inclure dans l'ingress N2 |
| `heritia.env.example` | Variables centralisées proxy + secrets Railway |

## Vérification après déploiement

```bash
# Doit renvoyer X-Heritia-App: 1 et {"status":"ok","app":"HERITIA"}
curl -sI https://heritia.neriacorp.com/health

# Doit renvoyer {"status":"ok","app":"HERITIA"} (pas n2-core)
curl -s https://heritia.neriacorp.com/api/health

# La page d'accueil doit contenir <title>HERITIA</title> (pas « NeriaCorp · N2 Core »)
curl -s https://heritia.neriacorp.com/ | grep -o '<title>[^<]*</title>'
```

## État actuel (diagnostic)

Au 2026-09-10, `heritia.neriacorp.com` sert encore le shell **NeriaCorp · N2 Core** et `/api/health` répond `n2-core`. Les actions manuelles ci-dessous sont requises pour basculer vers Heritia.

## Checklist actions manuelles

### 1. Cloudflare DNS

1. Ouvrir la zone DNS **neriacorp.com** dans Cloudflare.
2. Localiser l'enregistrement **`heritia`** (type `CNAME` ou `A`).
3. Si le CNAME pointe vers le service N2 Core global (`app.neriacorp.com`, `global.neriacorp.com`, ou IP ingress N2) **sans route tenant Heritia** : conserver le CNAME vers l'ingress N2 **mais** appliquer la route tenant (étape 2).
4. Mode proxy Cloudflare : **Proxied (nuage orange)** recommandé ; SSL/TLS → **Full (strict)** si certificat origin valide sur N2.
5. Ne pas créer de second enregistrement `heritia` en conflit.

### 2. Single Ingress N2 (NoyauNeria2.0)

1. Copier `infra/n2/heritia.tenant.json` dans le registre des tenants N2 (Catalog / Deploy Master / fichier routes selon votre déploiement N2).
2. Inclure `infra/n2/heritia.ingress.conf` dans la config nginx/Caddy du point d'entrée, **avant** le fallback shell N2 Core.
3. Définir `priority: 200` (ou supérieure au catch-all N2) pour que `heritia.neriacorp.com` ne tombe plus sur le shell PWA par défaut.
4. Charger les variables depuis `infra/n2/heritia.env.example` dans le secret manager N2 / Railway ingress.
5. Recharger l'ingress (`nginx -s reload` ou redéploiement du service N2).
6. Vérifier que `heritia.neriacorp.com/health` expose `X-Heritia-App: 1`.

### 3. Railway — service `heritia-web`

1. Projet Railway `lovely-expression`, service **`heritia-web`** (root `frontend/`).
2. S'assurer que le service est **déployé et actif** (au diagnostic, `heritia-web-production.up.railway.app` renvoyait 404).
3. **Ne pas** attacher le domaine custom `heritia.neriacorp.com` directement à `heritia-web` si le trafic passe par N2 (le domaine reste sur l'ingress N2).
4. Variables build Docker :
   - `VITE_API_URL=/api`
   - `VITE_APP_URL=https://heritia.neriacorp.com`
5. `PORT=3000` aligné avec le target port Railway interne.

### 4. Railway — service `heritia-api`

1. Service **`heritia-api`** (root `backend/`).
2. Variables runtime :
   - `HERITIA_ENVIRONMENT=production`
   - `HERITIA_APP_BASE_URL=https://heritia.neriacorp.com`
   - `HERITIA_FRONTEND_URL=https://heritia.neriacorp.com`
   - `HERITIA_CORS_ORIGINS=https://heritia.neriacorp.com,http://localhost:5174`
   - `N2_MASTER_KEY`, `RESEND_API_KEY`, clés Stripe/Cloudinary depuis le secret manager NeriaCorp.
3. Healthcheck Railway : `/api/health` → `{"status":"ok","app":"HERITIA"}`.

### 5. SSL/TLS

1. Si TLS est terminé sur **Cloudflare** : certificat origin sur N2 (Let's Encrypt ou Cloudflare Origin Certificate).
2. Si TLS est terminé sur **N2** : générer/renouveler le certificat pour `heritia.neriacorp.com` (certbot ou Cloudflare Origin CA).
3. Éviter le mode Flexible Cloudflare + origin HTTP non sécurisé en production.

### 6. Catalogue NeriaCorp (optionnel)

1. Publier `frontend/public/neriacorp-app.json` dans le catalogue apps N2 (zone B2C).
2. Vérifier que le portail NeriaCorp liste Heritia avec l'URL `https://heritia.neriacorp.com`.

### 7. Stripe webhooks (si actif)

1. Endpoint webhook Stripe : `https://heritia.neriacorp.com/api/marketplace/stripe/webhook` (ou route exacte de votre config).
2. Mettre à jour l'URL dans le dashboard Stripe si elle pointait encore vers Railway direct.

### 8. Test de non-régression N2

1. Confirmer que `app.neriacorp.com` sert toujours le Cockpit N2.
2. Confirmer que `mamandouce.neriacorp.com` n'est pas impacté.
3. Purger le cache Cloudflare pour `heritia.neriacorp.com` si l'ancien shell N2 est encore servi.
