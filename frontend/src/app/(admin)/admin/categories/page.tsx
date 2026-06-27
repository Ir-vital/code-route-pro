import type { Metadata } from "next";
import { CategoriesAdminView } from "@/features/admin/components/CategoriesAdminView";

export const metadata: Metadata = { title: "Gestion des catégories" };

export default function AdminCategoriesPage() {
  return <CategoriesAdminView />;
}
