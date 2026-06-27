"use client";

import { cn } from "@/lib/utils";
import { Clock } from "lucide-react";
import { useExamTimer } from "@/hooks/useExamTimer";

interface ExamTimerProps {
  timeLimitSeconds: number;
  onTimeUp: () => void;
}

export function ExamTimer({ timeLimitSeconds, onTimeUp }: ExamTimerProps) {
  const { formatted, isWarning } = useExamTimer(onTimeUp);

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg px-4 py-2 font-mono text-lg font-bold transition-colors",
        isWarning
          ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 animate-pulse"
          : "bg-muted text-foreground"
      )}
      role="timer"
      aria-label={`Temps restant : ${formatted}`}
    >
      <Clock size={18} className="shrink-0" />
      {formatted}
    </div>
  );
}
