# ADR-003 — FastAPI + SQLAlchemy 2.0 async

**Statut** : Accepté  
**Date** : 2026-06

---

## Contexte

Choix du framework web Python et de l'ORM pour le backend.

## Options considérées

| Critère | FastAPI | Django REST | Flask |
|---|---|---|---|
| Async natif | ✅ | Partiel | ❌ |
| Validation auto (Pydantic) | ✅ | Non | Non |
| OpenAPI auto-généré | ✅ | Plugin | Plugin |
| Performance | Très haute | Moyenne | Moyenne |
| Typage Python | Excellent | Moyen | Faible |

| Critère | SQLAlchemy 2.0 | Django ORM | Tortoise ORM |
|---|---|---|---|
| Async natif | ✅ (asyncpg) | Partiel | ✅ |
| Maturité | Très haute | Très haute | Moyenne |
| Typage `Mapped[]` | ✅ | ❌ | Partiel |

## Décision

**FastAPI + Pydantic v2 + SQLAlchemy 2.0 (style déclaratif + `Mapped[]`) + asyncpg.**

## Conséquences

✅ Validation des requêtes et réponses automatique via Pydantic.  
✅ Documentation Swagger/Redoc générée sans effort supplémentaire.  
✅ Requêtes DB entièrement asynchrones — pas de thread-blocking.  
✅ `Mapped[T]` compatible mypy/Pyright pour un typage fort.  
⚠️ SQLAlchemy 2.0 a une courbe d'apprentissage pour le style async. La documentation officielle reste la référence.
