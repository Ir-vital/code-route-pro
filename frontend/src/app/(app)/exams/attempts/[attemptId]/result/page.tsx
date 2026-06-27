import type { Metadata } from "next";

import { ExamResultView } from "@/features/exams/components/ExamResultView";

interface Props {
  params: Promise<{ attemptId: string }>;
}

export const metadata: Metadata = { title: "Résultat de l'examen" };

export default async function ExamResultPage({ params }: Props) {
  const { attemptId } = await params;
  return <ExamResultView attemptId={attemptId} />;
}
