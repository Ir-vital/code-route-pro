import { apiClient } from "@/lib/api/axios-client";

export interface DashboardSummary {
  total_attempts: number;
  completed_attempts: number;
  average_score: number | null;
  best_score: number | null;
  last_score: number | null;
  current_streak_days: number;
  xp_points: number;
  level: number;
}

export interface ProgressChartPoint {
  date: string;
  score: number;
}

export interface CategoryMastery {
  category_id: string;
  mastery_percentage: number;
}

export const dashboardApi = {
  getSummary: () =>
    apiClient.get<DashboardSummary>("/dashboard/summary").then((r) => r.data),

  getProgressChart: () =>
    apiClient.get<ProgressChartPoint[]>("/dashboard/progress-chart").then((r) => r.data),

  getCategoryMastery: () =>
    apiClient.get<CategoryMastery[]>("/dashboard/category-mastery").then((r) => r.data),

  getRecommendations: () =>
    apiClient.get("/dashboard/recommendations").then((r) => r.data),
};
