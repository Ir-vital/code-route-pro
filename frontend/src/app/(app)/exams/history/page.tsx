import type { Metadata } from "next";

import { ExamHistoryTable } from "@/features/exams/components/ExamHistoryTable";

export const metadata: Metadata = { title: "Historique des examens" };

export default function ExamHistoryPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Historique des tentatives</h1>
      <ExamHistoryTable />
    </div>
  );
}
