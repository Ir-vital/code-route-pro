"use client";

import { cn } from "@/lib/utils";
import { CheckCircle, Circle } from "lucide-react";

interface AnswerOptionProps {
  id: string;
  content: string;
  isSelected: boolean;
  isMultiple: boolean;
  onSelect: (optionId: string) => void;
  disabled?: boolean;
}

export function AnswerOption({
  id,
  content,
  isSelected,
  isMultiple,
  onSelect,
  disabled = false,
}: AnswerOptionProps) {
  return (
    <button
      onClick={() => !disabled && onSelect(id)}
      disabled={disabled}
      aria-pressed={isSelected}
      className={cn(
        "w-full flex items-start gap-3 rounded-xl border p-4 text-left text-sm transition-all",
        "hover:border-primary/60 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring",
        isSelected
          ? "border-primary bg-primary/10 dark:bg-primary/20"
          : "border-input bg-card",
        disabled && "cursor-not-allowed opacity-60"
      )}
    >
      <span className="mt-0.5 shrink-0">
        {isSelected ? (
          <CheckCircle size={18} className="text-primary" />
        ) : (
          <Circle size={18} className="text-muted-foreground" />
        )}
      </span>
      <span className="flex-1 leading-relaxed">{content}</span>
    </button>
  );
}
