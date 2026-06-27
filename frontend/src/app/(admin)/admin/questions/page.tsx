import type { Metadata } from "next";
import { QuestionsAdminView } from "@/features/admin/components/QuestionsAdminView";

export const metadata: Metadata = { title: "Gestion des questions" };

export default function AdminQuestionsPage() {
  return <QuestionsAdminView />;
}
