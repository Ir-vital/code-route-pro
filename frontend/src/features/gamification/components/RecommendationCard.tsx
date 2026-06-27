"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, X } from "lucide-react";
import Link from "next/link";
import { apiClient } from "@/lib/api/axios-client";

interface RecommendationCardProps {
  id: string;
  categoryId: string;
  categoryName: string;
  categorySlug: string;
  reason: string | null;
  masteryPct?: number;
}

export function RecommendationCard({
  id,
  categoryId,
  categoryName,
  categorySlug,
  reason,
  masteryPct,
}: RecommendationCardProps) {
  const qc = useQueryClient();
  const { mutate: dismiss } = useMutation({
    mutationFn: () => apiClient.post(`/recommendations/${id}/dismiss`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboard"] }),
  });

  return (
    <div className="flex items-start gap-3 rounded-xl border bg-card p-4 group">
      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium">{categoryName}</p>
          {masteryPct !== undefined && (
            <span className="text-xs text-muted-foreground">
              {masteryPct.toFixed(0)}% maîtrise
            </span>
          )}
        </div>
        {reason && (
          <p className="text-xs text-muted-foreground">{reason}</p>
        )}
      </div>
      <div className="flex items-center gap-1 shrink-0">
        <Link
          href={`/learn/${categorySlug}`}
          className="flex items-center gap-1 rounded-md bg-primary/10 text-primary px-2.5 py-1.5 text-xs font-medium hover:bg-primary/20 transition-colors"
        >
          Pratiquer
          <ArrowRight size={12} />
        </Link>
        <button
          onClick={() => dismiss()}
          className="rounded-md p-1.5 text-muted-foreground hover:bg-accent opacity-0 group-hover:opacity-100 transition-all"
          aria-label="Ignorer cette recommandation"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  );
}
