"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";
import { formatScore } from "@/lib/utils";

export function StatsAdminView() {
  const { data: examStats } = useQuery({
    queryKey: ["admin", "stats", "exams"],
    queryFn: () => apiClient.get("/admin/stats/exams").then((r) => r.data),
  });

  const { data: userStats } = useQuery({
    queryKey: ["admin", "stats", "users"],
    queryFn: () => apiClient.get("/admin/stats/users").then((r) => r.data),
  });

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Statistiques</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <h2 className="font-semibold">Utilisateurs</h2>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-muted-foreground">Total</dt><dd className="font-medium">{userStats?.total_users ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Actifs</dt><dd className="font-medium">{userStats?.active_users ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Vérifiés</dt><dd className="font-medium">{userStats?.verified_users ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Admins</dt><dd className="font-medium">{userStats?.admin_count ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Élèves</dt><dd className="font-medium">{userStats?.student_count ?? "—"}</dd></div>
          </dl>
        </div>

        <div className="rounded-xl border bg-card p-6 space-y-4">
          <h2 className="font-semibold">Examens</h2>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-muted-foreground">Tentatives totales</dt><dd className="font-medium">{examStats?.total_attempts ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Terminées</dt><dd className="font-medium">{examStats?.completed_attempts ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Réussies</dt><dd className="font-medium">{examStats?.pass_count ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Score moyen</dt><dd className="font-medium">{examStats?.average_score != null ? formatScore(examStats.average_score) : "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Taux de réussite</dt><dd className="font-medium">{examStats?.pass_rate != null ? formatScore(examStats.pass_rate) : "—"}</dd></div>
          </dl>
        </div>
      </div>
    </div>
  );
}
