/** Routes de l'application — source unique de vérité pour les chemins. */

export const ROUTES = {
  // Public
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",

  // App (élève)
  DASHBOARD: "/dashboard",
  LEARN: "/learn",
  CATEGORY: (slug: string) => `/learn/${slug}`,
  SIGN: (slug: string, signId: string) => `/learn/${slug}/${signId}`,
  FAVORITES: "/favorites",
  EXAMS: "/exams",
  EXAM_RUN: (examId: string, attemptId: string) => `/exams/${examId}/run?attempt=${attemptId}`,
  EXAM_RESULT: (attemptId: string) => `/exams/attempts/${attemptId}/result`,
  EXAM_HISTORY: "/exams/history",
  PROGRESS: "/progress",
  NOTIFICATIONS: "/notifications",
  PROFILE: "/profile",

  // Admin
  ADMIN: "/admin",
  ADMIN_USERS: "/admin/users",
  ADMIN_CATEGORIES: "/admin/categories",
  ADMIN_SIGNS: "/admin/signs",
  ADMIN_QUESTIONS: "/admin/questions",
  ADMIN_EXAMS: "/admin/exams",
  ADMIN_STATS: "/admin/stats",
} as const;
