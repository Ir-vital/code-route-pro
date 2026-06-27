/**
 * Middleware Next.js — protection des routes par authentification et rôle.
 *
 * Routes publiques   : /, /login, /register, /forgot-password, /reset-password
 * Routes authentifié : /dashboard, /learn/*, /exams/*, /favorites, /progress, ...
 * Routes admin       : /admin/*  (requiert role === "admin")
 */

import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = [
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
];

const ADMIN_PREFIX = "/admin";

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
}

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;

  // Ignorer les fichiers statiques et les API routes Next.js
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // Lire les tokens depuis les cookies (httpOnly cookies posés par le frontend)
  const accessToken = request.cookies.get("access_token")?.value;
  const userRole = request.cookies.get("user_role")?.value;

  // Chemin public → laisser passer (rediriger vers /dashboard si déjà connecté)
  if (isPublicPath(pathname)) {
    if (accessToken && pathname !== "/") {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  // Chemin protégé → vérifier l'authentification
  if (!accessToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Route admin → vérifier le rôle
  if (pathname.startsWith(ADMIN_PREFIX)) {
    if (userRole !== "admin") {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Appliquer le middleware sur toutes les routes sauf :
     * - _next/static (fichiers statiques)
     * - _next/image (optimisation d'images)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
