# HERITIA — module NoyauNeria (`backend/n2/heritia/`)

Routes exposées via `backend/routes/heritia.py` (prefix `/api/n2/heritia`).

## Endpoints

| Méthode | Route | Auth | Rôle |
|---------|-------|------|------|
| POST | `/scan` | `X-Master-Key` | Analyse image Cloudinary + XP/cagnotte |
| POST | `/recipes/generate` | `X-Master-Key` | Génération recettes + XP |
| POST | `/stripe/webhook` | `stripe-signature` (prod) | Déblocage ebooks achetés |
| GET | `/health` | — | Statut module |

## Payload scan

```json
{
  "user_id": 42,
  "scan_type": "fridge",
  "image_url": "https://res.cloudinary.com/<cloud>/image/upload/heritia/frigo.jpg"
}
```

Réponse : `ingredients[]` avec `name`, `quantity_estimate`, `expiry_date`, `expiry_hint`, plus `gamification` si `user_id` fourni.

## Variables requises

- `N2_MASTER_KEY` (ou `NERIA_MASTER_KEY` / `X_MASTER_KEY`)
- `CLOUDINARY_*` pour OCR Admin API
- `FIREBASE_PROJECT_ID` + `FIREBASE_CREDENTIALS_JSON` pour sync cagnotte
- `HERITIA_STRIPE_WEBHOOK_SECRET` pour webhook production

## Intégration NoyauNeria

Copier `backend/n2/heritia/` et `backend/routes/heritia.py` dans le repo N2, puis monter le router :

```python
from routes.heritia import router as heritia_router
app.include_router(heritia_router, prefix="/api")
```
