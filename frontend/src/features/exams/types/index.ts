export type ExamType = "practice" | "mock_official" | "category_focus";
export type AttemptStatus = "in_progress" | "completed" | "abandoned";
export type Difficulty = "easy" | "medium" | "hard" | "mixed";

export interface Exam {
  id: string;
  title: string;
  description: string | null;
  exam_type: ExamType;
  category_id: string | null;
  question_count: number;
  time_limit_seconds: number;
  passing_score_percentage: number;
  difficulty: Difficulty;
  is_active: boolean;
}

export interface AttemptSummary {
  id: string;
  exam_id: string;
  status: AttemptStatus;
  score_percentage: number | null;
  is_passed: boolean | null;
  started_at: string | null;
  finished_at: string | null;
  duration_seconds: number | null;
}

export interface AttemptState {
  id: string;
  exam_id: string;
  status: AttemptStatus;
  started_at: string | null;
  total_questions: number;
  answered_count: number;
}

export interface AnswerResult {
  question_id: string;
  question_content: string;
  is_correct: boolean;
  selected_option_ids: string[];
  correct_option_ids: string[];
  explanation: string | null;
}

export interface AttemptResult {
  attempt_id: string;
  exam_title: string;
  score_percentage: number;
  is_passed: boolean;
  duration_seconds: number | null;
  total_questions: number;
  correct_answers: number;
  finished_at: string | null;
  answers: AnswerResult[];
}
