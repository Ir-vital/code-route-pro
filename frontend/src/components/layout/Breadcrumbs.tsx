"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

const LABELS: Record<string, string> = {
  dashboard: "Tableau de bord",
  learn: "Apprendre",
  favorites: "Favoris",
  exams: "Examens",
  history: "Historique",
  run: "Examen en cours",
  result: "Résultat",
  attempts: "Tentatives",
  progress: "Progression",
  notifications: "Notifications",
  profile: "Profil",
  admin: "Administration",
  users: "Utilisateurs",
  categories: "Catégories",
  signs: "Panneaux",
  questions: "Questions",
  stats: "Statistiques",
};

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length <= 1) return null;

  const crumbs = segments.map((seg, i) => {
    const href = "/" + segments.slice(0, i + 1).join("/");
    const label = LABELS[seg] ?? (seg.length > 20 ? `${seg.slice(0, 8)}…` : seg);
    const isLast = i === segments.length - 1;
    return { href, label, isLast };
  });

  return (
    <nav aria-label="Fil d'Ariane" className="flex items-center gap-1 text-sm text-muted-foreground mb-4">
      <Link href="/dashboard" className="hover:text-foreground transition-colors">
        <Home size={14} />
        <span className="sr-only">Accueil</span>
      </Link>
      {crumbs.map((crumb) => (
        <span key={crumb.href} className="flex items-center gap-1">
          <ChevronRight size={14} className="shrink-0" />
          {crumb.isLast ? (
            <span className="text-foreground font-medium">{crumb.label}</span>
          ) : (
            <Link href={crumb.href} className="hover:text-foreground transition-colors">
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
