import type { Metadata } from "next";

import { NotificationList } from "@/features/notifications/components/NotificationList";

export const metadata: Metadata = { title: "Notifications" };

export default function NotificationsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Notifications</h1>
      <NotificationList />
    </div>
  );
}
