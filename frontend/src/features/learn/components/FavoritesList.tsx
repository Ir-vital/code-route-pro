"use client";

import Image from "next/image";
import Link from "next/link";
import { Heart } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { apiClient } from "@/lib/api/axios-client";
import { useMyFavorites, useToggleFavorite } from "../hooks/useLearn";
import { DifficultyBadge } from "./DifficultyBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { AnimatedList, AnimatedListItem } from "@/components/ui/AnimatedContainer";
import { Pagination } from "@/components/ui/Pagination";
import { useState } from "react";
import type { Sign } from "../types";

export function FavoritesList() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useMyFavorites(page);

  // Charger les données complètes des panneaux favoris
  const signIds = data?.items.map((f) => f.sign_id) ?? [];
  const { data: signsData } = useQuery({
    queryKey: ["signs-by-ids", signIds],
    queryFn: async () => {
      if (!signIds.length) return [] as Sign[];
      // Charger chaque panneau individuellement (ou batch si l'API le supporte)
      const results = await Promise.all(
        signIds.map((id) => apiClient.get<Sign>(`/signs/${id}`).then((r) => r.data))
      );
      return results;
    },
    enabled: signIds.length > 0,
  });

  if (isLoading) return <PageLoader />;

  if (!data?.items.length) {
    return (
      <EmptyState
        icon={Heart}
        title="Aucun favori pour l'instant"
        description="Consultez des panneaux et cliquez sur le cœur pour les ajouter à vos favoris."
        action={
          <Link href="/learn" className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90">
            Parcourir les panneaux
          </Link>
        }
      />
    );
  }

  const signMap = new Map((signsData ?? []).map((s) => [s.id, s]));

  return (
    <div className="space-y-6">
      <AnimatedList>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {data.items.map((fav) => {
            const sign = signMap.get(fav.sign_id);
            return (
              <AnimatedListItem key={fav.id}>
                <FavoriteSignCard favoriteId={fav.id} sign={sign} />
              </AnimatedListItem>
            );
          })}
        </div>
      </AnimatedList>

      {(data.pages ?? 1) > 1 && (
        <Pagination page={page} totalPages={data.pages} onPageChange={setPage} />
      )}
    </div>
  );
}

function FavoriteSignCard({
  favoriteId,
  sign,
}: {
  favoriteId: string;
  sign: Sign | undefined;
}) {
  const { mutate: toggle, isPending } = useToggleFavorite(sign?.id ?? "", true);

  if (!sign) {
    return (
      <div className="h-48 rounded-xl bg-muted animate-pulse" />
    );
  }

  return (
    <div className="group rounded-xl border bg-card overflow-hidden hover:shadow-md transition-all">
      <Link href={`/learn/${sign.category_id}/${sign.id}`}>
        <div className="relative h-32 bg-muted">
          <Image src={sign.image_url} alt={sign.name} fill className="object-contain p-2" />
        </div>
      </Link>
      <div className="p-3 space-y-1">
        <Link href={`/learn/${sign.category_id}/${sign.id}`}>
          <p className="text-sm font-medium line-clamp-2 group-hover:text-primary transition-colors">
            {sign.name}
          </p>
        </Link>
        <div className="flex items-center justify-between">
          {sign.official_code && (
            <p className="text-xs text-muted-foreground">{sign.official_code}</p>
          )}
          <DifficultyBadge difficulty={sign.difficulty} />
        </div>
        <button
          onClick={() => toggle()}
          disabled={isPending}
          className="flex items-center gap-1 text-xs text-red-500 hover:text-red-600 transition-colors mt-1"
          aria-label="Retirer des favoris"
        >
          <Heart size={12} className="fill-red-500" />
          Retirer
        </button>
      </div>
    </div>
  );
}
