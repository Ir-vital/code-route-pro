"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({ page, totalPages, onPageChange, className }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = buildPageRange(page, totalPages);

  return (
    <nav
      aria-label="Pagination"
      className={cn("flex items-center justify-center gap-1", className)}
    >
      <PageButton
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Page précédente"
      >
        <ChevronLeft size={16} />
      </PageButton>

      {pages.map((p, i) =>
        p === "…" ? (
          <span key={`ellipsis-${i}`} className="px-2 text-muted-foreground select-none">
            …
          </span>
        ) : (
          <PageButton
            key={p}
            onClick={() => onPageChange(p as number)}
            isActive={p === page}
            aria-label={`Page ${p}`}
            aria-current={p === page ? "page" : undefined}
          >
            {p}
          </PageButton>
        )
      )}

      <PageButton
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="Page suivante"
      >
        <ChevronRight size={16} />
      </PageButton>
    </nav>
  );
}

function PageButton({
  children,
  onClick,
  disabled,
  isActive,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { isActive?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex h-9 min-w-[36px] items-center justify-center rounded-md px-2 text-sm font-medium transition-colors",
        isActive
          ? "bg-primary text-primary-foreground"
          : "hover:bg-accent text-muted-foreground hover:text-accent-foreground",
        disabled && "opacity-40 pointer-events-none"
      )}
      {...props}
    >
      {children}
    </button>
  );
}

function buildPageRange(current: number, total: number): (number | "…")[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages: (number | "…")[] = [1];
  if (current > 3) pages.push("…");
  for (let p = Math.max(2, current - 1); p <= Math.min(total - 1, current + 1); p++) {
    pages.push(p);
  }
  if (current < total - 2) pages.push("…");
  pages.push(total);
  return pages;
}
