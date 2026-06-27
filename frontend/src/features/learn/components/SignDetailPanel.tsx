"use client";

import Image from "next/image";
import { Heart } from "lucide-react";
import { useSign, useMyFavorites, useToggleFavorite } from "../hooks/useLearn";
import { DifficultyBadge } from "./DifficultyBadge";

export function SignDetailPanel({ signId }: { signId: string }) {
  const { data: sign, isLoading } = useSign(signId);
  const { data: favs } = useMyFavorites();
  const isFavorite = favs?.items.some((f) => f.sign_id === signId) ?? false;
  const { mutate: toggle, isPending } = useToggleFavorite(signId, isFavorite);

  if (isLoading) return <div className="h-96 bg-muted animate-pulse rounded-xl" />;
  if (!sign) return <p>Panneau introuvable</p>;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="rounded-xl border bg-card overflow-hidden">
        <div className="relative h-64 bg-muted">
          <Image src={sign.image_url} alt={sign.name} fill className="object-contain p-4" />
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">{sign.name}</h1>
              {sign.official_code && (
                <p className="text-sm text-muted-foreground">Code : {sign.official_code}</p>
              )}
            </div>
            <button
              onClick={() => toggle()}
              disabled={isPending}
              className="rounded-full p-2 hover:bg-muted transition-colors"
              aria-label={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
            >
              <Heart className={isFavorite ? "fill-red-500 text-red-500" : "text-muted-foreground"} size={20} />
            </button>
          </div>
          <DifficultyBadge difficulty={sign.difficulty} />
          <div>
            <h2 className="font-semibold mb-1">Signification</h2>
            <p className="text-sm text-muted-foreground">{sign.meaning}</p>
          </div>
          {sign.rules && (
            <div>
              <h2 className="font-semibold mb-1">Règles associées</h2>
              <p className="text-sm text-muted-foreground">{sign.rules}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
