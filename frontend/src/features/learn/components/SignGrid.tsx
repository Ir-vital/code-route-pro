"use client";

import Image from "next/image";
import Link from "next/link";
import { useCategories, useSigns } from "../hooks/useLearn";
import type { Difficulty } from "../types";
import { DifficultyBadge } from "./DifficultyBadge";

interface Props {
  categorySlug?: string;
  search?: string;
  difficulty?: string;
}

export function SignGrid({ categorySlug, search, difficulty }: Props) {
  const { data: categories } = useCategories();
  const category = categories?.find((c) => c.slug === categorySlug);

  const { data, isLoading } = useSigns({
    category_id: category?.id,
    search,
    difficulty,
    page_size: 24,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {category && (
        <h1 className="text-3xl font-bold">{category.name}</h1>
      )}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {data?.items.map((sign) => (
          <Link
            key={sign.id}
            href={`/learn/${categorySlug}/${sign.id}`}
            className="group rounded-xl border bg-card overflow-hidden hover:shadow-md transition-all"
          >
            <div className="relative h-32 bg-muted">
              <Image
                src={sign.image_url}
                alt={sign.name}
                fill
                className="object-contain p-2"
              />
            </div>
            <div className="p-3 space-y-1">
              <p className="text-sm font-medium line-clamp-2 group-hover:text-primary">
                {sign.name}
              </p>
              {sign.official_code && (
                <p className="text-xs text-muted-foreground">{sign.official_code}</p>
              )}
              <DifficultyBadge difficulty={sign.difficulty} />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
