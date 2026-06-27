import type { Metadata } from "next";

import { ExamList } from "@/features/exams/components/ExamList";

export const metadata: Metadata = { title: "Examens" };

export default function ExamsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Examens disponibles</h1>
      <ExamList />
    </div>
  );
}
