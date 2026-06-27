"use client";

import Link from "next/link";
import { useCategories } from "../hooks/useLearn";

export function CategoryGrid() {
  const { data: categories, isLoading } = useCategories();

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-32 rounded-xl bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {categories?.map((cat) => (
        <Link
          key={cat.id}
          href={`/learn/${cat.slug}`}
          className="group flex flex-col items-center justify-center gap-2 rounded-xl border bg-card p-6 text-center hover:border-primary hover:shadow-md transition-all"
          style={{ borderLeftColor: cat.color ?? undefined, borderLeftWidth: cat.color ? 4 : undefined }}
        >
          {cat.icon && <span className="text-3xl">{cat.icon}</span>}
          <span className="font-medium text-sm group-hover:text-primary transition-colors">
            {cat.name}
          </span>
        </Link>
      ))}
    </div>
  );
}
