"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, Tag, Image, HelpCircle,
  ClipboardList, BarChart, LogOut,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useLogout } from "@/features/auth/hooks/useAuth";
import { ThemeToggle } from "./ThemeToggle";
import { ADMIN_NAV_ITEMS } from "@/config/constants";

const ICON_MAP: Record<string, React.ElementType> = {
  LayoutDashboard, Users, Tag, Image, HelpCircle, ClipboardList, BarChart,
};

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { mutate: logout } = useLogout();

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar admin */}
      <aside className="hidden md:flex w-64 flex-col border-r bg-card">
        <div className="flex h-16 items-center border-b px-6">
          <span className="font-bold text-primary">Admin — CodeRoute</span>
        </div>
        <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
          {ADMIN_NAV_ITEMS.map((item) => {
            const Icon = ICON_MAP[item.icon] ?? LayoutDashboard;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon size={18} className="shrink-0" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="border-t p-3">
          <button
            onClick={() => logout()}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-accent transition-colors"
          >
            <LogOut size={16} />
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Contenu */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center justify-end border-b bg-card px-6 gap-3">
          <ThemeToggle />
        </header>
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
