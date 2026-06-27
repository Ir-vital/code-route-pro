"use client";

import Link from "next/link";
import { Bell, Menu, LogOut } from "lucide-react";

import { useMe, useLogout } from "@/features/auth/hooks/useAuth";
import { ThemeToggle } from "./ThemeToggle";
import { useUIStore } from "@/stores/ui.store";

export function Navbar() {
  const { data: user } = useMe();
  const { mutate: logout } = useLogout();
  const { toggleSidebar } = useUIStore();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-card px-4 gap-3">
      {/* Mobile sidebar toggle */}
      <button
        onClick={toggleSidebar}
        className="rounded-lg p-2 text-muted-foreground hover:bg-accent md:hidden"
        aria-label="Menu"
      >
        <Menu size={20} />
      </button>

      <div className="flex-1" />

      <ThemeToggle />

      <Link
        href="/notifications"
        className="rounded-lg p-2 text-muted-foreground hover:bg-accent transition-colors"
        aria-label="Notifications"
      >
        <Bell size={20} />
      </Link>

      {user && (
        <div className="flex items-center gap-2">
          <Link
            href="/profile"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-accent transition-colors"
          >
            <div className="h-7 w-7 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <span className="hidden md:block font-medium">
              {user.first_name} {user.last_name}
            </span>
          </Link>
          <button
            onClick={() => logout()}
            className="rounded-lg p-2 text-muted-foreground hover:bg-accent transition-colors"
            aria-label="Déconnexion"
          >
            <LogOut size={18} />
          </button>
        </div>
      )}
    </header>
  );
}
