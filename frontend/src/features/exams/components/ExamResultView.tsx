"use client";

import { CheckCircle, XCircle } from "lucide-react";
import { cn, formatDuration, formatScore } from "@/lib/utils";
import { useAttemptResult } from "../hooks/useExams";

export function ExamResultView({ attemptId }: { attemptId: string }) {
  const { data: result, isLoading } = useAttemptResult(attemptId);

  if (isLoading) return <div className="h-64 bg-muted animate-pulse rounded-xl" />;
  if (!result) return <p>Résultat introuvable</p>;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Résumé */}
      <div className={cn(
        "rounded-xl border p-8 text-center space-y-3",
        result.is_passed ? "border-green-500 bg-green-50 dark:bg-green-900/20" : "border-red-400 bg-red-50 dark:bg-red-900/20"
      )}>
        {result.is_passed
          ? <CheckCircle className="mx-auto text-green-500" size={48} />
          : <XCircle className="mx-auto text-red-500" size={48} />
        }
        <p className="text-4xl font-bold">{formatScore(result.score_percentage)}</p>
        <p className="text-lg font-medium">{result.is_passed ? "Examen réussi !" : "Examen non validé"}</p>
        <p className="text-sm text-muted-foreground">
          {result.correct_answers} / {result.total_questions} bonnes réponses
          {result.duration_seconds && ` · ${formatDuration(result.duration_seconds)}`}
        </p>
      </div>

      {/* Correction détaillée */}
      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Correction</h2>
        {result.answers.map((a, i) => (
          <div key={a.question_id} className={cn(
            "rounded-lg border p-4 space-y-2",
            a.is_correct ? "border-green-300 bg-green-50/50 dark:bg-green-900/10" : "border-red-300 bg-red-50/50 dark:bg-red-900/10"
          )}>
            <div className="flex gap-2 items-start">
              {a.is_correct
                ? <CheckCircle className="text-green-500 shrink-0 mt-0.5" size={16} />
                : <XCircle className="text-red-500 shrink-0 mt-0.5" size={16} />
              }
              <p className="text-sm font-medium">
                {i + 1}. {a.question_content}
              </p>
            </div>
            {a.explanation && (
              <p className="text-xs text-muted-foreground ml-6">{a.explanation}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
