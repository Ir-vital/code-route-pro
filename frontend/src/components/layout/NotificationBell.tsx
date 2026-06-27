"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { Bell } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function NotificationBell() {
  const qc = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);

  // Compte les non-lues
  const { data } = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: () =>
      apiClient.get("/notifications?page=1&page_size=1").then((r) => {
        const items = r.data?.items ?? [];
        return items.filter((n: any) => !n.is_read).length;
      }),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  const unreadCount: number = data ?? 0;

  // Connexion WebSocket pour les push temps réel
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const wsUrl = API_URL.replace(/^http/, "ws");
    const ws = new WebSocket(`${wsUrl}/ws/notifications?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = () => {
      // Invalider le cache pour recharger les notifications
      qc.invalidateQueries({ queryKey: ["notifications"] });
    };

    ws.onopen = () => {
      const ping = setInterval(() => ws.readyState === WebSocket.OPEN && ws.send("ping"), 30_000);
      ws.addEventListener("close", () => clearInterval(ping));
    };

    return () => {
      ws.close();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <Link
      href="/notifications"
      className="relative rounded-lg p-2 text-muted-foreground hover:bg-accent transition-colors"
      aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} non lues)` : ""}`}
    >
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}
