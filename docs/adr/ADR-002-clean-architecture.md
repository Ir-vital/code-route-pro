# ADR-002 — Clean Architecture dans chaque module backend

**Statut** : Accepté  
**Date** : 2026-06

---

## Contexte

Au sein de chaque module du Modular Monolith (ADR-001), comment organiser le code pour garantir la testabilité, la maintenabilité et l'indépendance vis-à-vis des frameworks ?

## Options considérées

### Option A — Flat (services + models)
`services.py`, `models.py`, `routes.py` dans chaque module.

**Contre** : les services dépendent directement de SQLAlchemy et FastAPI, rendant les tests unitaires impossibles sans base de données.

### Option B — Clean Architecture (Ports & Adapters) ✅
4 couches par module : `domain/` → `application/` → `infrastructure/` → `api/`.

**Pour** : la logique métier (use cases) ne dépend de rien d'externe. Tests unitaires avec mocks de repositories en millisecondes. L'ORM est un détail d'infrastructure, pas une contrainte du domaine.

## Décision

**Option B — Clean Architecture.**

Règle de dépendance stricte :
```
api → application → domain
infrastructure → domain
```

Le domaine ne dépend jamais d'une librairie externe.

## Conséquences

✅ Use cases testables avec `AsyncMock` de repositories, sans base de données.  
✅ Possible de changer d'ORM (ex: tortoise-orm) sans toucher aux use cases.  
✅ Schémas Pydantic isolés dans `api/` — ne polluent pas le domaine.  
⚠️ Plus de fichiers par module. La verbosité est le prix de la testabilité.
