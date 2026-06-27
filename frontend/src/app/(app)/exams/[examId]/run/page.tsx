import type { Metadata } from "next";

import { ExamRunner } from "@/features/exams/components/ExamRunner";

interface Props {
  params: Promise<{ examId: string }>;
}

export const metadata: Metadata = { title: "Examen en cours" };

export default async function ExamRunPage({ params }: Props) {
  const { examId } = await params;
  return <ExamRunner examId={examId} />;
}
