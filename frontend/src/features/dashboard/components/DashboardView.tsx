"use client";

import { useQuery } from "@tanstack/react-query";
import { Trophy, Target, Flame, Star } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

import { dashboardApi } from "../api/dashboard.api";
import { formatScore } from "@/lib/utils";

function StatCard({ label, value, icon: Icon, color }: {
  label: string;
  value: string;
  icon: React.ElementType;
  color: string;
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

export function DashboardView() {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: dashboardApi.getSummary,
  });

  const { data: chartData } = useQuery({
    queryKey: ["dashboard", "chart"],
    queryFn: dashboardApi.getProgressChart,
  });

  if (loadingSummary) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 bg-muted animate-pulse rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Tableau de bord</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Examens passés"
          value={String(summary?.completed_attempts ?? 0)}
          icon={Target}
          color="bg-blue-500"
        />
        <StatCard
          label="Meilleur score"
          value={summary?.best_score != null ? formatScore(summary.best_score) : "—"}
          icon={Trophy}
          color="bg-yellow-500"
        />
        <StatCard
          label="Série en cours"
          value={`${summary?.current_streak_days ?? 0}j`}
          icon={Flame}
          color="bg-orange-500"
        />
        <StatCard
          label="Niveau"
          value={`Niv. ${summary?.level ?? 1}`}
          icon={Star}
          color="bg-purple-500"
        />
      </div>

      {/* Graphique d'évolution */}
      {chartData && chartData.length > 0 && (
        <div className="rounded-xl border bg-card p-6">
          <h2 className="font-semibold mb-4">Évolution des scores</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, "Score"]} />
              <Line
                type="monotone"
                dataKey="score"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
