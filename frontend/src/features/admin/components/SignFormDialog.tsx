"use client";

import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useZodForm } from "@/hooks/useZodForm";
import { apiClient } from "@/lib/api/axios-client";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useCategories } from "@/features/learn/hooks/useLearn";

const schema = z.object({
  name: z.string().min(1, "Requis"),
  category_id: z.string().uuid("Catégorie requise"),
  image_url: z.string().url("URL invalide"),
  meaning: z.string().min(1, "Requis"),
  official_code: z.string().optional(),
  rules: z.string().optional(),
  difficulty: z.enum(["easy", "medium", "hard"]),
});
type FormValues = z.infer<typeof schema>;

interface SignFormDialogProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  sign?: { id: string } & Partial<FormValues>;
}

export function SignFormDialog({ open, onOpenChange, sign }: SignFormDialogProps) {
  const qc = useQueryClient();
  const isEdit = !!sign;
  const { data: categories } = useCategories();

  const form = useZodForm({
    schema,
    values: sign
      ? { name: sign.name ?? "", category_id: sign.category_id ?? "", image_url: sign.image_url ?? "", meaning: sign.meaning ?? "", official_code: sign.official_code ?? "", rules: sign.rules ?? "", difficulty: sign.difficulty ?? "easy" }
      : { name: "", category_id: "", image_url: "", meaning: "", official_code: "", rules: "", difficulty: "easy" },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: FormValues) =>
      isEdit ? apiClient.patch(`/signs/${sign!.id}`, data) : apiClient.post("/signs", data),
    onSuccess: () => {
      toast.success(isEdit ? "Panneau mis à jour" : "Panneau créé");
      qc.invalidateQueries({ queryKey: ["signs"] });
      qc.invalidateQueries({ queryKey: ["admin", "signs"] });
      onOpenChange(false);
    },
    onError: (err: any) => toast.error(err?.response?.data?.error?.message ?? "Erreur"),
  });

  const errors = form.formState.errors;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent onClose={() => onOpenChange(false)}>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Modifier le panneau" : "Nouveau panneau"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={form.handleSubmit((d) => mutate(d))} className="space-y-3 mt-2">
          <div className="space-y-1">
            <Label>Nom du panneau</Label>
            <Input {...form.register("name")} />
            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Catégorie</Label>
              <Select {...form.register("category_id")}>
                <option value="">Sélectionner…</option>
                {categories?.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </Select>
              {errors.category_id && <p className="text-xs text-destructive">{errors.category_id.message}</p>}
            </div>
            <div className="space-y-1">
              <Label>Difficulté</Label>
              <Select {...form.register("difficulty")}>
                <option value="easy">Facile</option>
                <option value="medium">Moyen</option>
                <option value="hard">Difficile</option>
              </Select>
            </div>
          </div>
          <div className="space-y-1">
            <Label>URL de l'image</Label>
            <Input {...form.register("image_url")} placeholder="https://…" />
            {errors.image_url && <p className="text-xs text-destructive">{errors.image_url.message}</p>}
          </div>
          <div className="space-y-1">
            <Label>Code officiel</Label>
            <Input {...form.register("official_code")} placeholder="B1, A1…" />
          </div>
          <div className="space-y-1">
            <Label>Signification</Label>
            <Textarea {...form.register("meaning")} rows={2} />
            {errors.meaning && <p className="text-xs text-destructive">{errors.meaning.message}</p>}
          </div>
          <div className="space-y-1">
            <Label>Règles associées</Label>
            <Textarea {...form.register("rules")} rows={2} />
          </div>
          <DialogFooter>
            <button type="button" onClick={() => onOpenChange(false)} className="rounded-md border px-4 py-2 text-sm hover:bg-accent">Annuler</button>
            <button type="submit" disabled={isPending} className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
              {isPending ? "Enregistrement…" : isEdit ? "Mettre à jour" : "Créer"}
            </button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
