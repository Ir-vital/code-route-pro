"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, LayoutDashboard, BookOpen, ClipboardList, Heart, TrendingUp, Bell, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS } from "@/config/constants";
import { useLogout } from "@/features/auth/hooks/useAuth";

const ICON_MAP: Record<string, React.ElementType> = {
  LayoutDashboard, BookOpen, ClipboardList, Heart, TrendingUp, Bell, User,
};

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { mutate: logout } = useLogout();

  return (
    <>
      {/* Bouton hamburger */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden rounded-lg p-2 text-muted-foreground hover:bg-accent transition-colors"
        aria-label="Ouvrir le menu"
      >
        <Menu size={20} />
      </button>

      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Drawer */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 bg-card border-r flex flex-col transition-transform duration-300 md:hidden",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between h-16 border-b px-4">
          <span className="font-bold text-primary">CodeRoute Pro</span>
          <button
            onClick={() => setOpen(false)}
            className="rounded-lg p-2 text-muted-foreground hover:bg-accent"
            aria-label="Fermer le menu"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = ICON_MAP[item.icon] ?? LayoutDashboard;
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon size={18} className="shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t p-3">
          <button
            onClick={() => { logout(); setOpen(false); }}
            className="w-full rounded-lg px-3 py-2.5 text-sm text-muted-foreground hover:bg-accent text-left"
          >
            Déconnexion
          </button>
        </div>
      </aside>
    </>
  );
}
