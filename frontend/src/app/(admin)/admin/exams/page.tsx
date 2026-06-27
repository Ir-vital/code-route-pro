import type { Metadata } from "next";
import { ExamsAdminView } from "@/features/admin/components/ExamsAdminView";

export const metadata: Metadata = { title: "Gestion des examens" };

export default function AdminExamsPage() {
  return <ExamsAdminView />;
}
