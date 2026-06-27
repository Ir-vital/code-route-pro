import { Flame } from "lucide-react";
import { cn } from "@/lib/utils";

interface StreakCounterProps {
  currentStreak: number;
  longestStreak: number;
}

export function StreakCounter({ currentStreak, longestStreak }: StreakCounterProps) {
  const isHot = currentStreak >= 7;
  return (
    <div className="rounded-xl border bg-card p-4 flex items-center gap-4">
      <div className={cn(
        "flex h-12 w-12 items-center justify-center rounded-full",
        isHot ? "bg-orange-100 dark:bg-orange-900/30" : "bg-muted"
      )}>
        <Flame
          size={24}
          className={cn(isHot ? "text-orange-500" : "text-muted-foreground")}
        />
      </div>
      <div className="flex-1">
        <p className="text-xs text-muted-foreground">Série actuelle</p>
        <p className="text-2xl font-bold">
          {currentStreak}
          <span className="text-sm font-normal text-muted-foreground ml-1">
            jour{currentStreak > 1 ? "s" : ""}
          </span>
        </p>
      </div>
      <div className="text-right">
        <p className="text-xs text-muted-foreground">Record</p>
        <p className="text-lg font-semibold text-muted-foreground">{longestStreak}j</p>
      </div>
    </div>
  );
}
