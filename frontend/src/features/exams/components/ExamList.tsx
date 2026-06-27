"use client";

import { Clock, HelpCircle } from "lucide-react";
import { useExams, useStartExam } from "../hooks/useExams";
import { formatDuration } from "@/lib/utils";

export function ExamList() {
  const { data, isLoading } = useExams();
  const { mutate: start, isPending } = useStartExam();

  if (isLoading) {
    return (
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data?.items.map((exam) => (
        <div key={exam.id} className="rounded-xl border bg-card p-6 space-y-4 flex flex-col">
          <div className="flex-1 space-y-2">
            <h3 className="font-semibold">{exam.title}</h3>
            {exam.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">{exam.description}</p>
            )}
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <HelpCircle size={12} />
                {exam.question_count} questions
              </span>
              <span className="flex items-center gap-1">
                <Clock size={12} />
                {formatDuration(exam.time_limit_seconds)}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              Score requis : {exam.passing_score_percentage}%
            </p>
          </div>
          <button
            onClick={() => start(exam.id)}
            disabled={isPending}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            Commencer
          </button>
        </div>
      ))}
    </div>
  );
}
