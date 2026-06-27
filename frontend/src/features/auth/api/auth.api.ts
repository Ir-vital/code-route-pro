import { apiClient } from "@/lib/api/axios-client";
import type {
  AuthResponse,
  ForgotPasswordInput,
  LoginInput,
  RegisterInput,
  ResetPasswordInput,
  TokenPair,
  User,
} from "../types";

export const authApi = {
  register: (data: RegisterInput) =>
    apiClient.post<User>("/auth/register", data).then((r) => r.data),

  login: (data: LoginInput) =>
    apiClient.post<AuthResponse>("/auth/login", data).then((r) => r.data),

  logout: (refresh_token: string) =>
    apiClient.post("/auth/logout", { refresh_token }),

  refresh: (refresh_token: string) =>
    apiClient.post<TokenPair>("/auth/refresh", { refresh_token }).then((r) => r.data),

  forgotPassword: (data: ForgotPasswordInput) =>
    apiClient.post("/auth/forgot-password", data),

  resetPassword: (data: ResetPasswordInput) =>
    apiClient.post("/auth/reset-password", data),

  getMe: () => apiClient.get<User>("/auth/me").then((r) => r.data),
};
