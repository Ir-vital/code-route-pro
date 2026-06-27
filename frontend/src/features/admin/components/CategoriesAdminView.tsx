"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";

export function CategoriesAdminView() {
  const { data: categories, isLoading } = useQuery({
    queryKey: ["admin", "categories"],
    queryFn: () => apiClient.get("/categories?include_inactive=true").then((r) => r.data) as Promise<any[]>,
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Catégories</h1>
        <button className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground">
          + Nouvelle catégorie
        </button>
      </div>
      <div className="rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Nom</th>
              <th className="px-4 py-3 text-left font-medium">Slug</th>
              <th className="px-4 py-3 text-left font-medium">Ordre</th>
              <th className="px-4 py-3 text-left font-medium">Statut</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {categories?.map((c: any) => (
              <tr key={c.id} className="hover:bg-muted/30">
                <td className="px-4 py-3 font-medium">{c.name}</td>
                <td className="px-4 py-3 text-muted-foreground font-mono text-xs">{c.slug}</td>
                <td className="px-4 py-3">{c.display_order}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${c.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
                    {c.is_active ? "Actif" : "Inactif"}
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
