# Architecture Decision Records (ADRs)

Les ADRs documentent les décisions architecturales significatives prises pendant le développement de CodeRoute Pro. Chaque décision est numérotée, datée, et accompagnée de son contexte, des options considérées et de la justification du choix retenu.

## Format

Chaque ADR suit le template :
- **Statut** : Proposé | Accepté | Déprécié | Remplacé par ADR-XXX
- **Contexte** : Pourquoi cette décision était nécessaire
- **Options considérées** : Les alternatives évaluées
- **Décision** : Ce qui a été choisi
- **Conséquences** : Impact positif et négatif

## Index

| # | Titre | Statut | Date |
|---|---|---|---|
| [ADR-001](./ADR-001-modular-monolith.md) | Architecture Modular Monolith pour le backend | Accepté | 2026-06 |
| [ADR-002](./ADR-002-clean-architecture.md) | Clean Architecture dans chaque module | Accepté | 2026-06 |
| [ADR-003](./ADR-003-fastapi-sqlalchemy.md) | FastAPI + SQLAlchemy 2.0 async | Accepté | 2026-06 |
| [ADR-004](./ADR-004-nextjs-app-router.md) | Next.js 15 App Router + Feature-Based | Accepté | 2026-06 |
| [ADR-005](./ADR-005-jwt-refresh-tokens.md) | Stratégie JWT access + refresh tokens | Accepté | 2026-06 |
| [ADR-006](./ADR-006-redis-websocket.md) | Redis pub/sub pour WebSocket scalable | Accepté | 2026-06 |
| [ADR-007](./ADR-007-gestionnaire-dependances.md) | uv comme gestionnaire de dépendances Python | Accepté | 2026-06 |
