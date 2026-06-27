import type { Metadata } from "next";

import { SignGrid } from "@/features/learn/components/SignGrid";

interface Props {
  params: Promise<{ categorySlug: string }>;
  searchParams: Promise<{ search?: string; difficulty?: string }>;
}

export const metadata: Metadata = { title: "Panneaux" };

export default async function CategoryPage({ params, searchParams }: Props) {
  const { categorySlug } = await params;
  const { search, difficulty } = await searchParams;

  return (
    <div className="space-y-6">
      <SignGrid
        categorySlug={categorySlug}
        search={search}
        difficulty={difficulty}
      />
    </div>
  );
}
