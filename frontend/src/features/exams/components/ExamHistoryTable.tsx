"use client";

import Link from "next/link";
import { cn, formatDate, formatScore } from "@/lib/utils";
import { useExamHistory } from "../hooks/useExams";

export function ExamHistoryTable() {
  const { data, isLoading } = useExamHistory();

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;
  if (!data?.items.length) return <p className="text-muted-foreground">Aucune tentative pour l'instant.</p>;

  return (
    <div className="rounded-xl border overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-muted/50">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Date</th>
            <th className="px-4 py-3 text-left font-medium">Score</th>
            <th className="px-4 py-3 text-left font-medium">Résultat</th>
            <th className="px-4 py-3 text-left font-medium">Détails</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.items.map((attempt) => (
            <tr key={attempt.id} className="hover:bg-muted/30 transition-colors">
              <td className="px-4 py-3 text-muted-foreground">
                {attempt.started_at ? formatDate(attempt.started_at) : "—"}
              </td>
              <td className="px-4 py-3 font-medium">
                {attempt.score_percentage != null ? formatScore(attempt.score_percentage) : "—"}
              </td>
              <td className="px-4 py-3">
                {attempt.is_passed != null ? (
                  <span className={cn(
                    "inline-flex rounded-full px-2 py-0.5 text-xs font-medium",
                    attempt.is_passed
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  )}>
                    {attempt.is_passed ? "Réussi" : "Échoué"}
                  </span>
                ) : (
                  <span className="text-muted-foreground">En cours</span>
                )}
              </td>
              <td className="px-4 py-3">
                {attempt.status === "completed" && (
                  <Link
                    href={`/exams/attempts/${attempt.id}/result`}
                    className="text-primary hover:underline text-xs"
                  >
                    Voir
                  </Link>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
