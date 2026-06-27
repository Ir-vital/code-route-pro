"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { toast } from "sonner";

import { useAttempt, useSubmitAnswer, useSubmitAttempt } from "../hooks/useExams";
import { useExamStore } from "@/stores/exam.store";
import { apiClient } from "@/lib/api/axios-client";

import { QuestionCard } from "./QuestionCard";
import { ExamTimer } from "./ExamTimer";
import { ExamProgressBar } from "./ExamProgressBar";
import { ExamSubmitDialog } from "./ExamSubmitDialog";

interface AttemptQuestion {
  id: string;
  content: string;
  image_url?: string | null;
  question_type: "single_choice" | "multiple_choice";
  options: Array<{ id: string; content: string; display_order: number }>;
}

export function ExamRunner({ examId }: { examId: string }) {
  const searchParams = useSearchParams();
  const attemptId = searchParams.get("attempt") ?? "";

  const { data: attempt, isLoading: loadingAttempt } = useAttempt(attemptId);
  const { mutate: submitAnswer } = useSubmitAnswer(attemptId);
  const { mutate: submitAttempt, isPending: isSubmitting } = useSubmitAttempt();

  const { selectedOptions, selectOption, setAttempt, clearExam } = useExamStore();

  const [questions, setQuestions] = useState<AttemptQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);

  // Charger les questions de la tentative
  useEffect(() => {
    if (!attemptId) return;
    setLoadingQuestions(true);

    // Récupère les questions via l'endpoint examen + tentative
    // L'API retourne les questions sans is_correct (vue élève)
    apiClient
      .get(`/exams/attempts/${attemptId}/questions`)
      .then((r) => setQuestions(r.data))
      .catch(() => {
        // Fallback : pas de questions détaillées disponibles via cet endpoint
        // Le vrai endpoint serait à créer côté backend pour exposer les questions d'une tentative
      })
      .finally(() => setLoadingQuestions(false));
  }, [attemptId]);

  // Initialiser le timer quand la tentative est chargée
  useEffect(() => {
    if (attempt && attempt.total_questions > 0) {
      // Récupère la durée limite depuis l'examen
      apiClient.get(`/exams`).then((r) => {
        const exam = r.data?.items?.find((e: any) => e.id === examId);
        if (exam) {
          setAttempt(attemptId, exam.time_limit_seconds);
        }
      });
    }
    return () => clearExam();
  }, [attempt?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const currentQuestion = questions[currentIdx];
  const totalQuestions = attempt?.total_questions ?? questions.length;
  const answeredCount = Object.keys(selectedOptions).filter(
    (qId) => selectedOptions[qId]?.length > 0
  ).length;

  function handleSelectOption(optionId: string) {
    if (!currentQuestion) return;
    const isMultiple = currentQuestion.question_type === "multiple_choice";
    selectOption(currentQuestion.id, optionId, isMultiple);

    // Synchroniser avec le backend
    const newSelected = isMultiple
      ? selectedOptions[currentQuestion.id]?.includes(optionId)
        ? selectedOptions[currentQuestion.id].filter((id) => id !== optionId)
        : [...(selectedOptions[currentQuestion.id] ?? []), optionId]
      : [optionId];

    submitAnswer(
      { question_id: currentQuestion.id, selected_option_ids: newSelected },
      { onError: () => toast.error("Erreur lors de l'enregistrement de la réponse") }
    );
  }

  function handleTimeUp() {
    toast.warning("Temps écoulé ! L'examen est soumis automatiquement.");
    submitAttempt(attemptId);
  }

  function handleSubmitConfirm() {
    submitAttempt(attemptId);
    setShowSubmitDialog(false);
  }

  if (!attemptId) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-muted-foreground">Tentative introuvable.</p>
      </div>
    );
  }

  if (loadingAttempt || loadingQuestions) {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <div className="h-12 bg-muted animate-pulse rounded-xl" />
        <div className="h-64 bg-muted animate-pulse rounded-xl" />
      </div>
    );
  }

  return (
    <>
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header : timer + progression */}
        <div className="flex items-center justify-between gap-4 rounded-xl border bg-card p-4">
          <ExamTimer timeLimitSeconds={0} onTimeUp={handleTimeUp} />
          <div className="flex-1">
            <ExamProgressBar
              current={currentIdx}
              total={totalQuestions}
              answered={answeredCount}
            />
          </div>
        </div>

        {/* Question courante */}
        {currentQuestion ? (
          <div className="rounded-xl border bg-card p-6">
            <QuestionCard
              questionNumber={currentIdx + 1}
              totalQuestions={totalQuestions}
              content={currentQuestion.content}
              imageUrl={currentQuestion.image_url}
              questionType={currentQuestion.question_type}
              options={currentQuestion.options}
              selectedOptionIds={selectedOptions[currentQuestion.id] ?? []}
              onSelectOption={handleSelectOption}
            />
          </div>
        ) : (
          <div className="rounded-xl border bg-card p-6 text-center text-muted-foreground">
            {questions.length === 0
              ? "Les questions de cette tentative se chargent…"
              : "Aucune question disponible."}
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
            disabled={currentIdx === 0}
            className="flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-accent disabled:opacity-40 transition-colors"
          >
            <ChevronLeft size={16} />
            Précédente
          </button>

          <span className="text-sm text-muted-foreground">
            {currentIdx + 1} / {Math.max(totalQuestions, 1)}
          </span>

          {currentIdx < (Math.max(totalQuestions, 1) - 1) ? (
            <button
              onClick={() => setCurrentIdx((i) => Math.min(totalQuestions - 1, i + 1))}
              className="flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
            >
              Suivante
              <ChevronRight size={16} />
            </button>
          ) : (
            <button
              onClick={() => setShowSubmitDialog(true)}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Terminer l'examen
            </button>
          )}
        </div>

        {/* Grille de navigation rapide */}
        {totalQuestions > 1 && (
          <div className="rounded-xl border bg-card p-4 space-y-2">
            <p className="text-xs text-muted-foreground font-medium">Navigation rapide</p>
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: totalQuestions }).map((_, i) => {
                const qId = questions[i]?.id;
                const isAnswered = qId
                  ? (selectedOptions[qId]?.length ?? 0) > 0
                  : false;
                return (
                  <button
                    key={i}
                    onClick={() => setCurrentIdx(i)}
                    className={`h-8 w-8 rounded-lg text-xs font-medium transition-colors ${
                      i === currentIdx
                        ? "bg-primary text-primary-foreground"
                        : isAnswered
                        ? "bg-primary/20 text-primary border border-primary/30"
                        : "bg-muted text-muted-foreground hover:bg-accent"
                    }`}
                    aria-label={`Question ${i + 1}${isAnswered ? " (répondue)" : ""}`}
                  >
                    {i + 1}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Dialog de confirmation */}
      <ExamSubmitDialog
        isOpen={showSubmitDialog}
        totalQuestions={totalQuestions}
        answeredCount={answeredCount}
        isSubmitting={isSubmitting}
        onConfirm={handleSubmitConfirm}
        onCancel={() => setShowSubmitDialog(false)}
      />
    </>
  );
}
