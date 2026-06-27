import type { Metadata } from "next";
import { StatsAdminView } from "@/features/admin/components/StatsAdminView";

export const metadata: Metadata = { title: "Statistiques" };

export default function AdminStatsPage() {
  return <StatsAdminView />;
}
