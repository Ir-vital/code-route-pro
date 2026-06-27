"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useForgotPassword } from "../hooks/useAuth";

const schema = z.object({ email: z.string().email("Email invalide") });
type FormValues = z.infer<typeof schema>;

export function ForgotPasswordForm() {
  const { mutate, isPending, isSuccess } = useForgotPassword();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });

  if (isSuccess) {
    return (
      <div className="rounded-xl border bg-card p-8 shadow-sm text-center space-y-4">
        <p className="text-lg font-medium">Email envoyé !</p>
        <p className="text-sm text-muted-foreground">
          Si cet email est enregistré, vous recevrez un lien de réinitialisation.
        </p>
        <Link href="/login" className="text-primary hover:underline text-sm">Retour à la connexion</Link>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-8 shadow-sm space-y-6">
      <h1 className="text-2xl font-bold">Mot de passe oublié</h1>
      <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-medium">Email</label>
          <input {...register("email")} type="email" className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
          {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
        </div>
        <button type="submit" disabled={isPending} className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
          {isPending ? "Envoi..." : "Envoyer le lien"}
        </button>
      </form>
      <Link href="/login" className="block text-center text-sm text-primary hover:underline">Retour</Link>
    </div>
  );
}
