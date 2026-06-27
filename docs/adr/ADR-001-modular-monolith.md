# ADR-001 — Architecture Modular Monolith pour le backend

**Statut** : Accepté  
**Date** : 2026-06  
**Décideurs** : Équipe projet

---

## Contexte

CodeRoute Pro est une plateforme SaaS avec plusieurs domaines métier distincts : authentification, contenu pédagogique, examens, progression, gamification, notifications. La question de l'architecture backend s'est posée dès le départ : microservices, monolithe classique, ou autre ?

## Options considérées

### Option A — Microservices
Chaque domaine est un service indépendant avec sa propre base de données.

**Pour** : scalabilité indépendante, isolation des pannes, équipes autonomes.  
**Contre** : complexité opérationnelle massive pour une équipe réduite (service discovery, communication inter-services, transactions distribuées, observabilité). Prématuré pour un MVP.

### Option B — Monolithe classique (spaghetti)
Un seul déploiement, code non structuré.

**Pour** : simplicité initiale.  
**Contre** : dette technique rapide, difficile à tester, difficile à évoluer.

### Option C — Modular Monolith ✅
Un seul déploiement, mais découpé en modules métier autonomes avec leurs propres couches internes.

**Pour** : simplicité opérationnelle d'un monolithe + isolation des domaines. Chaque module peut être extrait en microservice sans réécriture totale. Adapté à une équipe réduite.  
**Contre** : discipline d'équipe nécessaire pour ne pas créer de dépendances cross-modules non désirées.

## Décision

**Option C — Modular Monolith.**

La règle de dépendance : un module ne peut importer que depuis `app/shared/` ou depuis ses propres couches. Les relations cross-module passent par des FK sur ID, jamais par import direct de domaine à domaine.

## Conséquences

✅ Un seul conteneur à déployer, une seule base de données, pas de latence réseau inter-services.  
✅ Tests d'intégration simples (une seule app à démarrer).  
✅ Évolution vers microservices possible module par module si le besoin se présente.  
⚠️ Nécessite une discipline de revue de code pour maintenir les frontières entre modules.
