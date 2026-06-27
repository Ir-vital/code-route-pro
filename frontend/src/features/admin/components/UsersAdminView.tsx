"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";
import { formatDate } from "@/lib/utils";

export function UsersAdminView() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "users"],
    queryFn: () => apiClient.get("/users/?page=1&page_size=50").then((r) => r.data),
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Utilisateurs</h1>
      <div className="rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Nom</th>
              <th className="px-4 py-3 text-left font-medium">Email</th>
              <th className="px-4 py-3 text-left font-medium">Rôle</th>
              <th className="px-4 py-3 text-left font-medium">Statut</th>
              <th className="px-4 py-3 text-left font-medium">Inscrit le</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data?.items?.map((u: any) => (
              <tr key={u.id} className="hover:bg-muted/30">
                <td className="px-4 py-3">{u.first_name} {u.last_name}</td>
                <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${u.role === "admin" ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"}`}>
                    {u.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${u.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {u.is_active ? "Actif" : "Inactif"}
                  </span>
                </td>
                <td className="px-4 py-3 text-muted-foreground">
                  {u.created_at ? formatDate(u.created_at) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
