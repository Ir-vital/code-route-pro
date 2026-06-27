"use client";

import { cn } from "@/lib/utils";
import { Star } from "lucide-react";

interface LevelIndicatorProps {
  level: number;
  xpPoints: number;
  xpPerLevel?: number;
}

export function LevelIndicator({ level, xpPoints, xpPerLevel = 100 }: LevelIndicatorProps) {
  const xpInCurrentLevel = xpPoints % xpPerLevel;
  const progressPct = Math.round((xpInCurrentLevel / xpPerLevel) * 100);

  return (
    <div className="rounded-xl border bg-card p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 border border-primary/30">
            <Star size={18} className="text-primary" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Niveau actuel</p>
            <p className="text-xl font-bold">{level}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">XP total</p>
          <p className="text-lg font-semibold text-primary">{xpPoints.toLocaleString("fr-FR")}</p>
        </div>
      </div>
      <XPProgressBar current={xpInCurrentLevel} max={xpPerLevel} level={level} />
    </div>
  );
}

export function XPProgressBar({
  current,
  max,
  level,
}: { current: number; max: number; level: number }) {
  const pct = Math.min(100, Math.round((current / max) * 100));
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{current} / {max} XP vers le niveau {level + 1}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
