import type { Metadata } from "next";

import { UsersAdminView } from "@/features/admin/components/UsersAdminView";

export const metadata: Metadata = { title: "Gestion des utilisateurs" };

export default function AdminUsersPage() {
  return <UsersAdminView />;
}
