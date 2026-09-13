# NSI (Neria Scout Intelligent) — persistance 100% N2 native

Pas de Firebase / Supabase pour ce module. Toute la persistance passe par le backend N2 (SQLite ou MongoDB via Railway).

## Principe d'autonomie stricte

Chaque projet NSI est une application **100% autonome**. Aucun pontage automatique de stock, de flux ou de données entre Heritia, Aevis, Selys et Selys Marketplace.

| Project ID | Application | Périmètre |
|---|---|---|
| `heritia-core` | Heritia | B2C — scan frigo/tickets, recettes, gamification XP, livres digitaux |
| `aevis-core` | Aevis | B2B — POS tactile, stock/inventaire commerçants C2 |
| `selys-core` | Selys | Mise en relation, recrutement direct, Direct-Pay, Zero-Retention casier |
| `selys-marketplace-core` | Selys Marketplace | Vitrine locale géolocalisée, livraison, Ventes Privées N2O (distinct de Selys core) |

## Seed au démarrage

`seed_nsi_defaults()` s'exécute au boot (`app/main.py`) et :

1. **Réinitialise** les 4 projets canoniques (écrase les données stale, ex. anciens tremplins Heritia → Selys)
2. **Supprime** les projets NSI hors registre canonique
3. **Purge** les signaux obsolètes (convergence B2B/marketplace cross-app)
4. **Injecte** un signal de veille par projet

Migration légère SQLite : ajout automatique des colonnes `target_audience` et `perimeter` si absentes.

## Endpoints API (`/api/n2/nsi/*`)

| Route | Auth | Rôle |
|---|---|---|
| `GET /projects` | — | Liste les 4 projets autonomes |
| `POST /projects` | `X-Master-Key` | Crée / met à jour un projet |
| `GET /signals` | — | Signaux de veille (filtre `?project_id=`) |
| `POST /signals/analyze` | `X-Master-Key` | Kit Fast-Track **scopé au projet** (pas de bridge Portail/Selys) |
| `GET /health` | — | Santé module NSI |

## Fast-Track autonome

Le kit Fast-Track (`build_fast_track_kit`) retourne des actions **recommandées au sein du périmètre du projet** :

- `target_audience`, `perimeter`
- `neria_radar_filters` (filtres NeriaRadar propres au projet)
- `recommended_actions` (plus de `portal_actions` / `selys_actions` cross-app)
- `recommended_mvp`, `export_label`

## Cockpit N2

Registre : `backend/n2/config_registry.py` → entrée `nsi` (`/console/nsi`).

UI : `backend/n2/cockpit/NsiDashboard.jsx` — cartes des 4 projets, export NeriaRadar par projet, signaux filtrés.

## Variables d'environnement

```env
N2_MASTER_KEY=<clé-NeriaCorp>
# Alias acceptés : NERIA_MASTER_KEY, X_MASTER_KEY
```

## Intégration NoyauNeria

```python
from routes.nsi import router as nsi_router
app.include_router(nsi_router, prefix="/api")
```

Copier `backend/n2/nsi/` et `backend/routes/nsi.py` dans le repo N2.
