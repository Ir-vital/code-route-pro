import { cn } from "@/lib/utils";
import type { Difficulty } from "../types";

const styles: Record<Difficulty, string> = {
  easy: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  hard: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

const labels: Record<Difficulty, string> = {
  easy: "Facile",
  medium: "Moyen",
  hard: "Difficile",
};

export function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  return (
    <span className={cn("inline-block rounded-full px-2 py-0.5 text-xs font-medium", styles[difficulty])}>
      {labels[difficulty]}
    </span>
  );
}
