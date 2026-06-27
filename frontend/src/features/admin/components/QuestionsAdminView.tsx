"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";

export function QuestionsAdminView() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "questions"],
    queryFn: () => apiClient.get("/questions?page_size=50").then((r) => r.data),
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Questions</h1>
        <button className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground">
          + Nouvelle question
        </button>
      </div>
      <div className="rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Question</th>
              <th className="px-4 py-3 text-left font-medium">Type</th>
              <th className="px-4 py-3 text-left font-medium">Difficulté</th>
              <th className="px-4 py-3 text-left font-medium">Options</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data?.items?.map((q: any) => (
              <tr key={q.id} className="hover:bg-muted/30">
                <td className="px-4 py-3 max-w-xs">
                  <p className="line-clamp-2 font-medium">{q.content}</p>
                </td>
                <td className="px-4 py-3 text-muted-foreground">{q.question_type}</td>
                <td className="px-4 py-3">{q.difficulty}</td>
                <td className="px-4 py-3 text-muted-foreground">{q.options?.length ?? 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
