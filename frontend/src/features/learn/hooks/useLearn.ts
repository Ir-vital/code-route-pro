"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { learnApi } from "../api/learn.api";

export const learnKeys = {
  categories: () => ["categories"] as const,
  signs: (params: object) => ["signs", params] as const,
  sign: (id: string) => ["signs", id] as const,
  favorites: (params: object) => ["favorites", params] as const,
};

export function useCategories() {
  return useQuery({
    queryKey: learnKeys.categories(),
    queryFn: learnApi.getCategories,
  });
}

export function useSigns(params: {
  page?: number;
  page_size?: number;
  category_id?: string;
  difficulty?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: learnKeys.signs(params),
    queryFn: () => learnApi.getSigns(params),
  });
}

export function useSign(id: string) {
  return useQuery({
    queryKey: learnKeys.sign(id),
    queryFn: () => learnApi.getSign(id),
    enabled: !!id,
  });
}

export function useMyFavorites(page = 1) {
  return useQuery({
    queryKey: learnKeys.favorites({ page }),
    queryFn: () => learnApi.getMyFavorites({ page }),
  });
}

export function useToggleFavorite(signId: string, isFavorite: boolean) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      isFavorite ? learnApi.removeFavorite(signId) : learnApi.addFavorite(signId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["favorites"] });
      toast.success(isFavorite ? "Retiré des favoris" : "Ajouté aux favoris");
    },
  });
}
