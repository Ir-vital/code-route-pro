"use client";

import { useMyFavorites } from "../hooks/useLearn";

export function FavoritesList() {
  const { data, isLoading } = useMyFavorites();

  if (isLoading) return <div className="h-32 bg-muted animate-pulse rounded-xl" />;
  if (!data?.items.length) return <p className="text-muted-foreground">Aucun panneau favori pour l'instant.</p>;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {data.items.map((fav) => (
        <div key={fav.id} className="rounded-xl border bg-card p-4 text-sm text-muted-foreground">
          Panneau {fav.sign_id.slice(0, 8)}…
        </div>
      ))}
    </div>
  );
}
