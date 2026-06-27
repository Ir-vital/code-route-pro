"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, CheckCheck } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";
import { apiClient } from "@/lib/api/axios-client";

export function NotificationList() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => apiClient.get("/notifications").then((r) => r.data),
  });

  const { mutate: markAllRead } = useMutation({
    mutationFn: () => apiClient.patch("/notifications/read-all"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const { mutate: markRead } = useMutation({
    mutationFn: (id: string) => apiClient.patch(`/notifications/${id}/read`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  if (isLoading) return <div className="h-48 bg-muted animate-pulse rounded-xl" />;

  const items = data?.items ?? [];
  const unread = items.filter((n: any) => !n.is_read).length;

  return (
    <div className="space-y-4">
      {unread > 0 && (
        <div className="flex justify-end">
          <button
            onClick={() => markAllRead()}
            className="flex items-center gap-1 text-sm text-primary hover:underline"
          >
            <CheckCheck size={14} />
            Tout marquer comme lu
          </button>
        </div>
      )}

      {!items.length ? (
        <p className="text-muted-foreground">Aucune notification.</p>
      ) : (
        <div className="space-y-2">
          {items.map((n: any) => (
            <div
              key={n.id}
              className={cn(
                "rounded-xl border p-4 flex gap-3 transition-colors",
                !n.is_read && "bg-primary/5 border-primary/20"
              )}
            >
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium">{n.title}</p>
                <p className="text-sm text-muted-foreground">{n.message}</p>
                <p className="text-xs text-muted-foreground">{formatDate(n.created_at)}</p>
              </div>
              {!n.is_read && (
                <button
                  onClick={() => markRead(n.id)}
                  className="text-muted-foreground hover:text-primary transition-colors"
                  aria-label="Marquer comme lu"
                >
                  <Check size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
