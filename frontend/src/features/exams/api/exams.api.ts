import { apiClient } from "@/lib/api/axios-client";
import type { AttemptResult, AttemptState, AttemptSummary, Exam } from "../types";
import type { PaginatedResponse } from "@/features/learn/types";

export const examsApi = {
  getExams: (params?: { page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Exam>>("/exams", { params }).then((r) => r.data),

  startAttempt: (examId: string) =>
    apiClient.post<AttemptState>(`/exams/${examId}/start`).then((r) => r.data),

  getAttempt: (attemptId: string) =>
    apiClient.get<AttemptState>(`/exams/attempts/${attemptId}`).then((r) => r.data),

  submitAnswer: (attemptId: string, data: { question_id: string; selected_option_ids: string[] }) =>
    apiClient.post(`/exams/attempts/${attemptId}/answer`, data),

  submitAttempt: (attemptId: string) =>
    apiClient.post<AttemptResult>(`/exams/attempts/${attemptId}/submit`).then((r) => r.data),

  getResult: (attemptId: string) =>
    apiClient.get<AttemptResult>(`/exams/attempts/${attemptId}/result`).then((r) => r.data),

  getHistory: (params?: { page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<AttemptSummary>>("/exams/attempts", { params }).then((r) => r.data),
};
