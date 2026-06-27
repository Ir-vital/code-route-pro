/**
 * Store Zustand pour l'état local d'un examen en cours.
 * Timer côté client, réponses en attente de synchronisation.
 */

import { create } from "zustand";

interface ExamState {
  attemptId: string | null;
  timeRemainingSeconds: number;
  selectedOptions: Record<string, string[]>; // questionId → optionIds
  setAttempt: (id: string, timeLimitSeconds: number) => void;
  tick: () => void;
  selectOption: (questionId: string, optionId: string, isMultiple: boolean) => void;
  clearExam: () => void;
}

export const useExamStore = create<ExamState>()((set) => ({
  attemptId: null,
  timeRemainingSeconds: 0,
  selectedOptions: {},

  setAttempt: (id, timeLimitSeconds) =>
    set({ attemptId: id, timeRemainingSeconds: timeLimitSeconds, selectedOptions: {} }),

  tick: () =>
    set((s) => ({ timeRemainingSeconds: Math.max(0, s.timeRemainingSeconds - 1) })),

  selectOption: (questionId, optionId, isMultiple) =>
    set((s) => {
      const current = s.selectedOptions[questionId] ?? [];
      let next: string[];
      if (isMultiple) {
        next = current.includes(optionId)
          ? current.filter((id) => id !== optionId)
          : [...current, optionId];
      } else {
        next = [optionId];
      }
      return { selectedOptions: { ...s.selectedOptions, [questionId]: next } };
    }),

  clearExam: () =>
    set({ attemptId: null, timeRemainingSeconds: 0, selectedOptions: {} }),
}));
