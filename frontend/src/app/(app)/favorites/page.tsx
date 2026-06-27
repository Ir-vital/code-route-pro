import type { Metadata } from "next";

import { FavoritesList } from "@/features/learn/components/FavoritesList";

export const metadata: Metadata = { title: "Mes favoris" };

export default function FavoritesPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Mes panneaux favoris</h1>
      <FavoritesList />
    </div>
  );
}
