import type { Metadata } from "next";

import { AdminDashboard } from "@/features/admin/components/AdminDashboard";

export const metadata: Metadata = { title: "Administration" };

export default function AdminPage() {
  return <AdminDashboard />;
}
