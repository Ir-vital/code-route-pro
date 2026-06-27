"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";
import { formatDuration } from "@/lib/utils";

export function ExamsAdminView() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "exams"],
    queryFn: () => apiClient.get("/exams?page_size=50").then((r) => r.data),
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Examens</h1>
        <button className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground">
          + Nouvel examen
        </button>
      </div>
      <div className="rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Titre</th>
              <th className="px-4 py-3 text-left font-medium">Type</th>
              <th className="px-4 py-3 text-left font-medium">Questions</th>
              <th className="px-4 py-3 text-left font-medium">Durée</th>
              <th className="px-4 py-3 text-left font-medium">Seuil</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data?.items?.map((e: any) => (
              <tr key={e.id} className="hover:bg-muted/30">
                <td className="px-4 py-3 font-medium">{e.title}</td>
                <td className="px-4 py-3 text-muted-foreground">{e.exam_type}</td>
                <td className="px-4 py-3">{e.question_count}</td>
                <td className="px-4 py-3">{formatDuration(e.time_limit_seconds)}</td>
                <td className="px-4 py-3">{e.passing_score_percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
