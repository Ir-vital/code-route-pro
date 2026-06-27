import type { Metadata } from "next";
import { SignsAdminView } from "@/features/admin/components/SignsAdminView";

export const metadata: Metadata = { title: "Gestion des panneaux" };

export default function AdminSignsPage() {
  return <SignsAdminView />;
}
