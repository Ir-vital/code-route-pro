"use client";

import { useQuery } from "@tanstack/react-query";
import { Users, BookOpen, TrendingUp, FileText } from "lucide-react";
import { apiClient } from "@/lib/api/axios-client";
import { formatScore } from "@/lib/utils";

function KpiCard({ label, value, icon: Icon, color }: {
  label: string; value: string; icon: React.ElementType; color: string;
}) {
  return (
    <div className="rounded-xl border bg-card p-5 flex items-center gap-4">
      <div className={`rounded-full p-3 ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  );
}

export function AdminDashboard() {
  const { data: overview } = useQuery({
    queryKey: ["admin", "overview"],
    queryFn: () => apiClient.get("/admin/stats/overview").then((r) => r.data),
  });

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Administration</h1>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Utilisateurs"
          value={String(overview?.total_users ?? "—")}
          icon={Users}
          color="bg-blue-500"
        />
        <KpiCard
          label="Actifs"
          value={String(overview?.active_users ?? "—")}
          icon={TrendingUp}
          color="bg-green-500"
        />
        <KpiCard
          label="Examens passés"
          value={String(overview?.total_exams_taken ?? "—")}
          icon={BookOpen}
          color="bg-purple-500"
        />
        <KpiCard
          label="Taux de réussite"
          value={overview?.average_success_rate != null ? formatScore(overview.average_success_rate) : "—"}
          icon={FileText}
          color="bg-orange-500"
        />
      </div>
    </div>
  );
}
