"use client";

import Image from "next/image";
import { AnswerOption } from "./AnswerOption";

interface Option {
  id: string;
  content: string;
  display_order: number;
}

interface QuestionCardProps {
  questionNumber: number;
  totalQuestions: number;
  content: string;
  imageUrl?: string | null;
  questionType: "single_choice" | "multiple_choice";
  options: Option[];
  selectedOptionIds: string[];
  onSelectOption: (optionId: string) => void;
  disabled?: boolean;
}

export function QuestionCard({
  questionNumber,
  totalQuestions,
  content,
  imageUrl,
  questionType,
  options,
  selectedOptionIds,
  onSelectOption,
  disabled = false,
}: QuestionCardProps) {
  const isMultiple = questionType === "multiple_choice";

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Question {questionNumber} / {totalQuestions}
          {isMultiple && (
            <span className="ml-2 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 px-2 py-0.5">
              Plusieurs réponses possibles
            </span>
          )}
        </p>
        <p className="text-lg font-medium leading-relaxed">{content}</p>
      </div>

      {/* Image optionnelle */}
      {imageUrl && (
        <div className="relative h-48 w-full rounded-xl overflow-hidden bg-muted">
          <Image src={imageUrl} alt="Illustration de la question" fill className="object-contain p-2" />
        </div>
      )}

      {/* Options */}
      <div className="space-y-3">
        {[...options]
          .sort((a, b) => a.display_order - b.display_order)
          .map((opt) => (
            <AnswerOption
              key={opt.id}
              id={opt.id}
              content={opt.content}
              isSelected={selectedOptionIds.includes(opt.id)}
              isMultiple={isMultiple}
              onSelect={onSelectOption}
              disabled={disabled}
            />
          ))}
      </div>
    </div>
  );
}
