"use client";

interface ExamProgressBarProps {
  current: number;   // index 0-based de la question affichée
  total: number;
  answered: number;  // nb de questions ayant au moins une réponse
}

export function ExamProgressBar({ current, total, answered }: ExamProgressBarProps) {
  const pct = total > 0 ? Math.round((answered / total) * 100) : 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{answered} / {total} réponses</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all duration-300"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {/* Indicateurs de questions */}
      <div className="flex gap-1 flex-wrap pt-1">
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 min-w-[8px] rounded-full transition-colors ${
              i === current
                ? "bg-primary"
                : i < total && answered > i
                ? "bg-primary/40"
                : "bg-muted-foreground/20"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
