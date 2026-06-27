export const APP_NAME = "CodeRoute Pro";

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

export const EXAM = {
  MIN_PASSING_SCORE: 80,
  WARNING_TIME_SECONDS: 60,
} as const;

export const XP_PER_LEVEL = 100;

export const NAV_ITEMS = [
  { label: "Tableau de bord", href: "/dashboard", icon: "LayoutDashboard" },
  { label: "Apprendre", href: "/learn", icon: "BookOpen" },
  { label: "Examens", href: "/exams", icon: "ClipboardList" },
  { label: "Favoris", href: "/favorites", icon: "Heart" },
  { label: "Progression", href: "/progress", icon: "TrendingUp" },
  { label: "Notifications", href: "/notifications", icon: "Bell" },
  { label: "Profil", href: "/profile", icon: "User" },
] as const;

export const ADMIN_NAV_ITEMS = [
  { label: "Vue d'ensemble", href: "/admin", icon: "LayoutDashboard" },
  { label: "Utilisateurs", href: "/admin/users", icon: "Users" },
  { label: "Catégories", href: "/admin/categories", icon: "Tag" },
  { label: "Panneaux", href: "/admin/signs", icon: "Image" },
  { label: "Questions", href: "/admin/questions", icon: "HelpCircle" },
  { label: "Examens", href: "/admin/exams", icon: "ClipboardList" },
  { label: "Statistiques", href: "/admin/stats", icon: "BarChart" },
] as const;
