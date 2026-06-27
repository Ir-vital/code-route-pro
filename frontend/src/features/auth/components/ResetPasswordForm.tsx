"use client";

import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useResetPassword } from "../hooks/useAuth";

const schema = z.object({
  new_password: z.string().min(8).regex(/[A-Z]/).regex(/[0-9]/),
});
type FormValues = z.infer<typeof schema>;

export function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const { mutate, isPending } = useResetPassword();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });

  return (
    <div className="rounded-xl border bg-card p-8 shadow-sm space-y-6">
      <h1 className="text-2xl font-bold">Nouveau mot de passe</h1>
      <form onSubmit={handleSubmit((d) => mutate({ token, new_password: d.new_password }))} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-medium">Nouveau mot de passe</label>
          <input {...register("new_password")} type="password" className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
          {errors.new_password && <p className="text-xs text-destructive">8 caractères min, 1 majuscule, 1 chiffre</p>}
        </div>
        <button type="submit" disabled={isPending || !token} className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
          {isPending ? "Enregistrement..." : "Réinitialiser"}
        </button>
      </form>
    </div>
  );
}
