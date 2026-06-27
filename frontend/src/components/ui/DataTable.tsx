"use client";

import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { Pagination } from "./Pagination";
import { EmptyState } from "./EmptyState";
import { LoadingSpinner } from "./LoadingSpinner";

export interface Column<T> {
  key: keyof T | string;
  header: string;
  sortable?: boolean;
  className?: string;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  searchable?: boolean;
  searchPlaceholder?: string;
  pageSize?: number;
  emptyTitle?: string;
  emptyDescription?: string;
  actions?: (row: T) => React.ReactNode;
}

type SortDir = "asc" | "desc" | null;

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  isLoading = false,
  searchable = true,
  searchPlaceholder = "Rechercher…",
  pageSize = 20,
  emptyTitle = "Aucun résultat",
  emptyDescription,
  actions,
}: DataTableProps<T>) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);
  const [page, setPage] = useState(1);

  // ─── Filtrage ─────────────────────────────────────────────────────────────
  const filtered = useMemo(() => {
    if (!search.trim()) return data;
    const q = search.toLowerCase();
    return data.filter((row) =>
      Object.values(row).some((v) => String(v ?? "").toLowerCase().includes(q))
    );
  }, [data, search]);

  // ─── Tri ──────────────────────────────────────────────────────────────────
  const sorted = useMemo(() => {
    if (!sortKey || !sortDir) return filtered;
    return [...filtered].sort((a, b) => {
      const av = String(a[sortKey] ?? "");
      const bv = String(b[sortKey] ?? "");
      const cmp = av.localeCompare(bv, "fr", { numeric: true });
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [filtered, sortKey, sortDir]);

  // ─── Pagination ───────────────────────────────────────────────────────────
  const totalPages = Math.ceil(sorted.length / pageSize);
  const paginated = sorted.slice((page - 1) * pageSize, page * pageSize);

  function handleSort(key: string) {
    if (sortKey !== key) {
      setSortKey(key);
      setSortDir("asc");
    } else if (sortDir === "asc") {
      setSortDir("desc");
    } else {
      setSortKey(null);
      setSortDir(null);
    }
    setPage(1);
  }

  function SortIcon({ colKey }: { colKey: string }) {
    if (sortKey !== colKey) return <ChevronsUpDown size={14} className="text-muted-foreground/50" />;
    return sortDir === "asc"
      ? <ChevronUp size={14} className="text-primary" />
      : <ChevronDown size={14} className="text-primary" />;
  }

  return (
    <div className="space-y-4">
      {searchable && (
        <div className="relative max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder={searchPlaceholder}
            className="w-full rounded-md border bg-background pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      )}

      <div className="rounded-xl border overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : paginated.length === 0 ? (
          <EmptyState title={emptyTitle} description={emptyDescription} className="border-0 rounded-none" />
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                {columns.map((col) => (
                  <th
                    key={String(col.key)}
                    className={cn("px-4 py-3 text-left font-medium whitespace-nowrap", col.className)}
                  >
                    {col.sortable ? (
                      <button
                        onClick={() => handleSort(String(col.key))}
                        className="flex items-center gap-1 hover:text-foreground transition-colors"
                      >
                        {col.header}
                        <SortIcon colKey={String(col.key)} />
                      </button>
                    ) : (
                      col.header
                    )}
                  </th>
                ))}
                {actions && <th className="px-4 py-3 text-left font-medium">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y">
              {paginated.map((row, i) => (
                <tr key={i} className="hover:bg-muted/30 transition-colors">
                  {columns.map((col) => (
                    <td key={String(col.key)} className={cn("px-4 py-3", col.className)}>
                      {col.render ? col.render(row) : String(row[col.key as keyof T] ?? "—")}
                    </td>
                  ))}
                  {actions && <td className="px-4 py-3">{actions(row)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{sorted.length} résultat{sorted.length > 1 ? "s" : ""}</span>
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      )}
    </div>
  );
}
