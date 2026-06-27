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

const schema = z.object({
  name: z.string().min(1, "Requis"),
  slug: z.string().min(1, "Requis").regex(/^[a-z0-9-]+$/, "Minuscules, chiffres et tirets uniquement"),
  description: z.string().optional(),
  icon: z.string().optional(),
  color: z.string().optional(),
  display_order: z.coerce.number().int().min(0),
});
type FormValues = z.infer<typeof schema>;

interface CategoryFormDialogProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  category?: { id: string } & FormValues;
}

export function CategoryFormDialog({ open, onOpenChange, category }: CategoryFormDialogProps) {
  const qc = useQueryClient();
  const isEdit = !!category;

  const form = useZodForm({
    schema,
    values: category ?? { name: "", slug: "", description: "", icon: "", color: "", display_order: 0 },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: FormValues) =>
      isEdit
        ? apiClient.patch(`/categories/${category!.id}`, data)
        : apiClient.post("/categories", data),
    onSuccess: () => {
      toast.success(isEdit ? "Catégorie mise à jour" : "Catégorie créée");
      qc.invalidateQueries({ queryKey: ["admin", "categories"] });
      qc.invalidateQueries({ queryKey: ["categories"] });
      onOpenChange(false);
    },
    onError: (err: any) => toast.error(err?.response?.data?.error?.message ?? "Erreur"),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent onClose={() => onOpenChange(false)}>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Modifier la catégorie" : "Nouvelle catégorie"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={form.handleSubmit((d) => mutate(d))} className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1 col-span-2">
              <Label>Nom</Label>
              <Input {...form.register("name")} />
              {form.formState.errors.name && <p className="text-xs text-destructive">{form.formState.errors.name.message}</p>}
            </div>
            <div className="space-y-1 col-span-2">
              <Label>Slug</Label>
              <Input {...form.register("slug")} placeholder="ex: panneaux-danger" />
              {form.formState.errors.slug && <p className="text-xs text-destructive">{form.formState.errors.slug.message}</p>}
            </div>
            <div className="space-y-1">
              <Label>Icône (emoji)</Label>
              <Input {...form.register("icon")} placeholder="⚠️" />
            </div>
            <div className="space-y-1">
              <Label>Couleur (hex)</Label>
              <Input {...form.register("color")} placeholder="#FF6B35" />
            </div>
            <div className="space-y-1">
              <Label>Ordre d'affichage</Label>
              <Input {...form.register("display_order")} type="number" min={0} />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Description</Label>
            <Textarea {...form.register("description")} rows={2} />
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
