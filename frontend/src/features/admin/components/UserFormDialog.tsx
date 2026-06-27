"use client";

import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useZodForm } from "@/hooks/useZodForm";
import { apiClient } from "@/lib/api/axios-client";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";

const schema = z.object({
  first_name: z.string().min(1, "Requis"),
  last_name: z.string().min(1, "Requis"),
  is_active: z.enum(["true", "false"]),
});
type FormValues = z.infer<typeof schema>;

interface UserFormDialogProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  user?: { id: string; first_name: string; last_name: string; is_active: boolean };
}

export function UserFormDialog({ open, onOpenChange, user }: UserFormDialogProps) {
  const qc = useQueryClient();
  const form = useZodForm({
    schema,
    values: user
      ? { first_name: user.first_name, last_name: user.last_name, is_active: String(user.is_active) as "true" | "false" }
      : { first_name: "", last_name: "", is_active: "true" },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: FormValues) =>
      apiClient.patch(`/users/${user?.id}`, {
        first_name: data.first_name,
        last_name: data.last_name,
        is_active: data.is_active === "true",
      }),
    onSuccess: () => {
      toast.success("Utilisateur mis à jour");
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      onOpenChange(false);
    },
    onError: () => toast.error("Erreur lors de la mise à jour"),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent onClose={() => onOpenChange(false)}>
        <DialogHeader>
          <DialogTitle>Modifier l'utilisateur</DialogTitle>
        </DialogHeader>
        <form onSubmit={form.handleSubmit((d) => mutate(d))} className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="first_name">Prénom</Label>
              <Input id="first_name" {...form.register("first_name")} />
              {form.formState.errors.first_name && (
                <p className="text-xs text-destructive">{form.formState.errors.first_name.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="last_name">Nom</Label>
              <Input id="last_name" {...form.register("last_name")} />
            </div>
          </div>
          <div className="space-y-1">
            <Label htmlFor="is_active">Statut</Label>
            <Select id="is_active" {...form.register("is_active")}>
              <option value="true">Actif</option>
              <option value="false">Inactif</option>
            </Select>
          </div>
          <DialogFooter>
            <button type="button" onClick={() => onOpenChange(false)} className="rounded-md border px-4 py-2 text-sm hover:bg-accent">Annuler</button>
            <button type="submit" disabled={isPending} className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
              {isPending ? "Enregistrement…" : "Enregistrer"}
            </button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
