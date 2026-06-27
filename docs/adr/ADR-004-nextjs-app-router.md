# ADR-004 — Next.js 15 App Router + Feature-Based Architecture

**Statut** : Accepté  
**Date** : 2026-06

---

## Contexte

Choix du framework frontend et de la structure d'organisation du code React.

## Options considérées

### Framework
- **Next.js 15 App Router** : SSR/SSG/ISR, Server Components, routing basé sur le filesystem.
- **Vite + React SPA** : Plus simple, mais pas de SSR, SEO limité.
- **Remix** : Bon routing, moins d'écosystème.

### Structure du code
- **Par type** : `components/`, `hooks/`, `services/` — Classique mais difficile à naviguer quand le projet grandit.
- **Feature-Based** : `features/auth/`, `features/exams/` — Chaque feature contient tout ce qui la concerne.

## Décision

**Next.js 15 App Router + Feature-Based Architecture.**

Les pages (`src/app/**`) restent minces : elles orchestrent uniquement des composants importés depuis `src/features/*`. Aucune logique métier dans les fichiers de route.

L'état serveur est géré par TanStack Query. Zustand est réservé à l'état UI pur (sidebar, timer d'examen).

## Conséquences

✅ SEO natif pour la landing page marketing.  
✅ Route Groups `(auth)`, `(app)`, `(admin)` permettent des layouts distincts sans impact sur les URLs.  
✅ Feature colocation : tout ce qui concerne `exams` est dans `features/exams/`.  
✅ Server Components pour les pages qui n'ont pas besoin de JS côté client.  
⚠️ App Router a une courbe d'apprentissage (Server vs Client Components, caching agressif).
