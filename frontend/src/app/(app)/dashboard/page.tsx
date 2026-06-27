import type { Metadata } from "next";

import { DashboardView } from "@/features/dashboard/components/DashboardView";

export const metadata: Metadata = { title: "Tableau de bord" };

export default function DashboardPage() {
  return <DashboardView />;
}
