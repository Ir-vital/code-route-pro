"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { apiClient } from "@/lib/api/axios-client";
import { useMe, AUTH_KEY } from "../hooks/useAuth";

const schema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
});
type FormValues = z.infer<typeof schema>;

export function ProfileView() {
  const { data: user } = useMe();
  const qc = useQueryClient();

  const { register, handleSubmit } = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: { first_name: user?.first_name ?? "", last_name: user?.last_name ?? "" },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: FormValues) =>
      apiClient.patch("/users/me", data).then((r) => r.data),
    onSuccess: (updated) => {
      qc.setQueryData(AUTH_KEY, updated);
      toast.success("Profil mis à jour");
    },
  });

  if (!user) return null;

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-3xl font-bold">Mon profil</h1>
      <div className="rounded-xl border bg-card p-6 space-y-4">
        <p className="text-sm text-muted-foreground">{user.email}</p>
        <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-sm font-medium">Prénom</label>
              <input {...register("first_name")} className="w-full rounded-md border px-3 py-2 text-sm" />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Nom</label>
              <input {...register("last_name")} className="w-full rounded-md border px-3 py-2 text-sm" />
            </div>
          </div>
          <button type="submit" disabled={isPending} className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {isPending ? "Enregistrement..." : "Enregistrer"}
          </button>
        </form>
      </div>
    </div>
  );
}
