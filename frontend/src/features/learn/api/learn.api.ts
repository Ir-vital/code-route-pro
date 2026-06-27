import { apiClient } from "@/lib/api/axios-client";
import type { Category, Favorite, PaginatedResponse, Sign } from "../types";

export const learnApi = {
  getCategories: () =>
    apiClient.get<Category[]>("/categories").then((r) => r.data),

  getSigns: (params: {
    page?: number;
    page_size?: number;
    category_id?: string;
    difficulty?: string;
    search?: string;
  }) =>
    apiClient.get<PaginatedResponse<Sign>>("/signs", { params }).then((r) => r.data),

  getSign: (id: string) =>
    apiClient.get<Sign>(`/signs/${id}`).then((r) => r.data),

  addFavorite: (signId: string) =>
    apiClient.post(`/signs/${signId}/favorite`),

  removeFavorite: (signId: string) =>
    apiClient.delete(`/signs/${signId}/favorite`),

  getMyFavorites: (params: { page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Favorite>>("/users/me/favorites", { params }).then((r) => r.data),
};
