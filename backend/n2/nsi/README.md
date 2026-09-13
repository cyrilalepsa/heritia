# NSI (Neria Scout Intelligent) — persistance 100% N2 native

Pas de Firebase / Supabase pour ce module. Toute la persistance passe par le backend N2 (SQLite ou MongoDB via Railway).

## 3 projets piliers autonomes

Chaque pilier est **100% indépendant** — aucun pontage de stock ou de flux entre Heritia, Aevis et Selys.

| Project ID | Pilier | Périmètre |
|---|---|---|
| `heritia-core` | Heritia (B2C) | Scan frigo/tickets, recettes, gamification XP, ebooks |
| `aevis-core` | Aevis (B2B) | POS tactile, stock/inventaire commerçants C2 |
| `selys-core` | Selys (écosystème unifié) | 2 volets intégrés : Service/Recrutement + Marketplace |

### Selys — écosystème unifié (`selys-core`)

Selys et Selys Marketplace sont regroupés sous **un seul projet canonique** avec deux volets indissociables (`integrated_modules`) :

1. **Volet Service & Recrutement** — Mise en relation, jobbing, CDD/CDI direct, Direct-Pay, Zero-Retention casier
2. **Volet Commercial & Vitrine (Marketplace)** — Vitrine géolocalisée, Click & Collect, livraison, Ventes Privées N2O

## Seed au démarrage

`seed_nsi_defaults()` s'exécute au boot (`app/main.py`) et :

1. **Réinitialise** les 3 projets piliers canoniques
2. **Supprime** `selys-marketplace-core` et tout projet hors registre
3. **Purge** les signaux obsolètes et re-attache les signaux marketplace à `selys-core`
4. **Injecte** les volets intégrés Selys via `integrated_modules`

Migration légère SQLite : colonnes `target_audience`, `perimeter`, `integrated_modules` si absentes.

## Endpoints API (`/api/n2/nsi/*`)

| Route | Auth | Rôle |
|---|---|---|
| `GET /projects` | — | Liste les 3 projets piliers |
| `POST /projects` | `X-Master-Key` | Crée / met à jour un projet |
| `GET /signals` | — | Signaux de veille (filtre `?project_id=`) |
| `POST /signals/analyze` | `X-Master-Key` | Kit Fast-Track scopé au projet |
| `GET /health` | — | Santé module NSI |

## Cockpit N2

UI : `backend/n2/cockpit/NsiDashboard.jsx` — grille 3 piliers, volets Selys visibles sur la carte unifiée.

## Intégration NoyauNeria

```python
from routes.nsi import router as nsi_router
app.include_router(nsi_router, prefix="/api")
```

Copier `backend/n2/nsi/` et `backend/routes/nsi.py` dans le repo N2.
