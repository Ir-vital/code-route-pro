import type { Metadata } from "next";

import { CategoryGrid } from "@/features/learn/components/CategoryGrid";

export const metadata: Metadata = { title: "Apprendre" };

export default function LearnPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Catégories de panneaux</h1>
      <CategoryGrid />
    </div>
  );
}
