"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { authApi } from "../api/auth.api";
import type { LoginInput, RegisterInput } from "../types";

export const AUTH_KEY = ["auth", "me"] as const;

function persistTokens(access: string, refresh: string, role: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
  document.cookie = `access_token=${access}; path=/; samesite=lax`;
  document.cookie = `user_role=${role}; path=/; samesite=lax`;
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  document.cookie = "access_token=; path=/; max-age=0";
  document.cookie = "user_role=; path=/; max-age=0";
}

export function useMe() {
  return useQuery({
    queryKey: AUTH_KEY,
    queryFn: authApi.getMe,
    staleTime: Infinity,
    retry: false,
  });
}

export function useLogin() {
  const router = useRouter();
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginInput) => authApi.login(data),
    onSuccess: (result) => {
      persistTokens(
        result.tokens.access_token,
        result.tokens.refresh_token,
        result.user.role
      );
      qc.setQueryData(AUTH_KEY, result.user);
      router.push("/dashboard");
    },
    onError: () => {
      toast.error("Email ou mot de passe incorrect");
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: RegisterInput) => authApi.register(data),
    onSuccess: () => {
      toast.success("Compte créé ! Connectez-vous pour continuer.");
      router.push("/login");
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error?.message ?? "Erreur lors de la création du compte";
      toast.error(msg);
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) await authApi.logout(refresh);
    },
    onSettled: () => {
      clearTokens();
      qc.clear();
      router.push("/login");
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: authApi.forgotPassword,
    onSuccess: () => {
      toast.success("Si cet email existe, un lien vous a été envoyé.");
    },
  });
}

export function useResetPassword() {
  const router = useRouter();

  return useMutation({
    mutationFn: authApi.resetPassword,
    onSuccess: () => {
      toast.success("Mot de passe réinitialisé. Connectez-vous.");
      router.push("/login");
    },
    onError: () => {
      toast.error("Lien invalide ou expiré.");
    },
  });
}
