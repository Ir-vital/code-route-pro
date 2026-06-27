# Seeds — CodeRoute Pro

Données initiales à insérer après `alembic upgrade head`.

## Ordre d'exécution

```
01_admin_user.sql   — Compte administrateur par défaut
02_categories.sql   — 8 catégories de panneaux
03_badges.sql       — 10 badges de gamification
04_exams.sql        — Examens blancs + entraînements par catégorie
```

## Exécution

```bash
# Depuis le dossier database/seeds/
psql $DATABASE_URL -f 01_admin_user.sql
psql $DATABASE_URL -f 02_categories.sql
psql $DATABASE_URL -f 03_badges.sql
psql $DATABASE_URL -f 04_exams.sql
```

Ou via Docker :

```bash
docker compose exec postgres psql -U coderoute -d coderoute_db -f /seeds/01_admin_user.sql
```

## Notes

- Le mot de passe de l'admin est `Admin1234` — **à changer immédiatement en production**.
- Les panneaux (`signs`) et questions (`questions`) ne sont pas seedés ici car ils
  constituent le contenu métier principal — à importer via l'interface admin ou un script dédié.
- Tous les seeds sont idempotents (`ON CONFLICT DO NOTHING`).
