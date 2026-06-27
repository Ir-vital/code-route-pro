"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { examsApi } from "../api/exams.api";

export const examKeys = {
  list: (p?: object) => ["exams", p] as const,
  attempt: (id: string) => ["attempt", id] as const,
  result: (id: string) => ["result", id] as const,
  history: (p?: object) => ["history", p] as const,
};

export function useExams(page = 1) {
  return useQuery({
    queryKey: examKeys.list({ page }),
    queryFn: () => examsApi.getExams({ page }),
  });
}

export function useStartExam() {
  const router = useRouter();
  return useMutation({
    mutationFn: (examId: string) => examsApi.startAttempt(examId),
    onSuccess: (attempt) => {
      router.push(`/exams/${attempt.exam_id}/run?attempt=${attempt.id}`);
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.error?.message ?? "Impossible de démarrer l'examen");
    },
  });
}

export function useAttempt(attemptId: string) {
  return useQuery({
    queryKey: examKeys.attempt(attemptId),
    queryFn: () => examsApi.getAttempt(attemptId),
    enabled: !!attemptId,
  });
}

export function useSubmitAnswer(attemptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { question_id: string; selected_option_ids: string[] }) =>
      examsApi.submitAnswer(attemptId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: examKeys.attempt(attemptId) });
    },
  });
}

export function useSubmitAttempt() {
  const router = useRouter();
  return useMutation({
    mutationFn: (attemptId: string) => examsApi.submitAttempt(attemptId),
    onSuccess: (result) => {
      router.push(`/exams/attempts/${result.attempt_id}/result`);
    },
  });
}

export function useAttemptResult(attemptId: string) {
  return useQuery({
    queryKey: examKeys.result(attemptId),
    queryFn: () => examsApi.getResult(attemptId),
    enabled: !!attemptId,
  });
}

export function useExamHistory(page = 1) {
  return useQuery({
    queryKey: examKeys.history({ page }),
    queryFn: () => examsApi.getHistory({ page }),
  });
}
