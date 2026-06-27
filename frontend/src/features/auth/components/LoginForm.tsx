"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { useLogin } from "../hooks/useAuth";

const schema = z.object({
  email: z.string().email("Email invalide"),
  password: z.string().min(1, "Mot de passe requis"),
});

type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const { mutate: login, isPending } = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  return (
    <div className="rounded-xl border bg-card p-8 shadow-sm space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold">Connexion</h1>
        <p className="text-sm text-muted-foreground">
          Bienvenue sur CodeRoute Pro
        </p>
      </div>

      <form onSubmit={handleSubmit((d) => login(d))} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-medium">Email</label>
          <input
            {...register("email")}
            type="email"
            placeholder="jean@example.com"
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {errors.email && (
            <p className="text-xs text-destructive">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium">Mot de passe</label>
          <input
            {...register("password")}
            type="password"
            placeholder="••••••••"
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {errors.password && (
            <p className="text-xs text-destructive">{errors.password.message}</p>
          )}
        </div>

        <div className="flex justify-end">
          <Link href="/forgot-password" className="text-xs text-primary hover:underline">
            Mot de passe oublié ?
          </Link>
        </div>

        <button
          type="submit"
          disabled={isPending}
          className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          {isPending ? "Connexion..." : "Se connecter"}
        </button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        Pas de compte ?{" "}
        <Link href="/register" className="text-primary hover:underline font-medium">
          Créer un compte
        </Link>
      </p>
    </div>
  );
}
