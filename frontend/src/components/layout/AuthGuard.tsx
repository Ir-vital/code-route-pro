"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useMe } from "@/features/auth/hooks/useAuth";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { UserRole } from "@/features/auth/types";

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  redirectTo?: string;
}

/**
 * Composant de garde côté client.
 * Complète le middleware Next.js pour les vérifications dynamiques.
 */
export function AuthGuard({
  children,
  requiredRole,
  redirectTo = "/login",
}: AuthGuardProps) {
  const { data: user, isLoading, isError } = useMe();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (isError || !user) {
      router.replace(redirectTo);
      return;
    }
    if (requiredRole && user.role !== requiredRole) {
      router.replace("/dashboard");
    }
  }, [user, isLoading, isError, requiredRole, redirectTo, router]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) return null;
  if (requiredRole && user.role !== requiredRole) return null;

  return <>{children}</>;
}
