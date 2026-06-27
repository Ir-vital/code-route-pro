"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";

export function SignsAdminView() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "signs"],
    queryFn: () => apiClient.get("/signs?page_size=50").then((r) => r.data),
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Panneaux</h1>
        <button className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground">
          + Nouveau panneau
        </button>
      </div>
      <div className="rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Nom</th>
              <th className="px-4 py-3 text-left font-medium">Code</th>
              <th className="px-4 py-3 text-left font-medium">Difficulté</th>
              <th className="px-4 py-3 text-left font-medium">Statut</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data?.items?.map((s: any) => (
              <tr key={s.id} className="hover:bg-muted/30">
                <td className="px-4 py-3 font-medium">{s.name}</td>
                <td className="px-4 py-3 text-muted-foreground font-mono text-xs">{s.official_code ?? "—"}</td>
                <td className="px-4 py-3">{s.difficulty}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs ${s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
                    {s.is_active ? "Actif" : "Inactif"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
