"use client";

import { AlertTriangle } from "lucide-react";

interface ExamSubmitDialogProps {
  isOpen: boolean;
  totalQuestions: number;
  answeredCount: number;
  isSubmitting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ExamSubmitDialog({
  isOpen,
  totalQuestions,
  answeredCount,
  isSubmitting,
  onConfirm,
  onCancel,
}: ExamSubmitDialogProps) {
  if (!isOpen) return null;

  const unanswered = totalQuestions - answeredCount;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="submit-dialog-title"
    >
      <div className="w-full max-w-md rounded-2xl border bg-card p-6 shadow-xl space-y-4 mx-4">
        <div className="flex items-start gap-3">
          {unanswered > 0 && (
            <AlertTriangle className="text-yellow-500 shrink-0 mt-0.5" size={20} />
          )}
          <div>
            <h2 id="submit-dialog-title" className="text-lg font-semibold">
              Terminer l'examen ?
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              {answeredCount} / {totalQuestions} questions répondues.
              {unanswered > 0 && (
                <span className="text-yellow-600 dark:text-yellow-400 font-medium">
                  {" "}{unanswered} question{unanswered > 1 ? "s" : ""} sans réponse.
                </span>
              )}
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground">
          Une fois soumis, vous ne pourrez plus modifier vos réponses.
        </p>

        <div className="flex gap-3 justify-end pt-2">
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors disabled:opacity-50"
          >
            Continuer l'examen
          </button>
          <button
            onClick={onConfirm}
            disabled={isSubmitting}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isSubmitting ? "Soumission..." : "Confirmer et soumettre"}
          </button>
        </div>
      </div>
    </div>
  );
}
