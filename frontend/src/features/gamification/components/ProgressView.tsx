"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";

export function ProgressView() {
  const { data: badges, isLoading } = useQuery({
    queryKey: ["badges", "me"],
    queryFn: () => apiClient.get("/badges/me").then((r) => r.data) as Promise<any[]>,
  });

  const { data: catalog } = useQuery({
    queryKey: ["badges"],
    queryFn: () => apiClient.get("/badges").then((r) => r.data) as Promise<any[]>,
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Ma progression</h1>

      {/* Badges obtenus */}
      <section>
        <h2 className="text-xl font-semibold mb-4">
          Mes badges ({badges?.length ?? 0})
        </h2>
        {!badges?.length ? (
          <p className="text-muted-foreground text-sm">
            Aucun badge encore. Continuez à vous entraîner !
          </p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {badges.map((ub: any) => (
              <div key={ub.badge.id} className="rounded-xl border bg-card p-4 text-center space-y-2">
                {ub.badge.icon && <span className="text-3xl">{ub.badge.icon}</span>}
                <p className="text-sm font-medium">{ub.badge.name}</p>
                <p className="text-xs text-muted-foreground">{ub.badge.description}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Catalogue badges */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Badges à débloquer</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {catalog?.map((b: any) => {
            const earned = badges?.some((ub: any) => ub.badge.id === b.id);
            return (
              <div
                key={b.id}
                className={`rounded-xl border p-4 text-center space-y-2 ${earned ? "opacity-40" : ""}`}
              >
                {b.icon && <span className="text-3xl">{b.icon}</span>}
                <p className="text-sm font-medium">{b.name}</p>
                <p className="text-xs text-muted-foreground">
                  {b.criteria_type === "exam_count" && `${b.criteria_value} examens`}
                  {b.criteria_type === "perfect_score" && `${b.criteria_value} score parfait`}
                  {b.criteria_type === "streak" && `${b.criteria_value} jours de suite`}
                  {b.criteria_type === "category_mastery" && `${b.criteria_value}% maîtrise`}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
