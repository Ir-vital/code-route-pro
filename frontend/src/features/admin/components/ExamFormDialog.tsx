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

const schema = z.object({
  title: z.string().min(1, "Requis"),
  exam_type: z.enum(["practice", "mock_official", "category_focus"]),
  difficulty: z.enum(["easy", "medium", "hard", "mixed"]),
  question_count: z.coerce.number().int().min(1).max(100),
  time_limit_seconds: z.coerce.number().int().min(60),
  passing_score_percentage: z.coerce.number().min(0).max(100),
  description: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

interface ExamFormDialogProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  exam?: { id: string } & Partial<FormValues>;
}

export function ExamFormDialog({ open, onOpenChange, exam }: ExamFormDialogProps) {
  const qc = useQueryClient();
  const isEdit = !!exam;

  const form = useZodForm({
    schema,
    values: exam
      ? { title: exam.title ?? "", exam_type: exam.exam_type ?? "practice", difficulty: exam.difficulty ?? "mixed", question_count: exam.question_count ?? 20, time_limit_seconds: exam.time_limit_seconds ?? 1200, passing_score_percentage: exam.passing_score_percentage ?? 80, description: exam.description ?? "" }
      : { title: "", exam_type: "practice", difficulty: "mixed", question_count: 20, time_limit_seconds: 1200, passing_score_percentage: 80, description: "" },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: FormValues) =>
      isEdit ? apiClient.patch(`/exams/${exam!.id}`, data) : apiClient.post("/exams", data),
    onSuccess: () => {
      toast.success(isEdit ? "Examen mis à jour" : "Examen créé");
      qc.invalidateQueries({ queryKey: ["exams"] });
      qc.invalidateQueries({ queryKey: ["admin", "exams"] });
      onOpenChange(false);
    },
    onError: (err: any) => toast.error(err?.response?.data?.error?.message ?? "Erreur"),
  });

  const errors = form.formState.errors;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent onClose={() => onOpenChange(false)}>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Modifier l'examen" : "Nouvel examen"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={form.handleSubmit((d) => mutate(d))} className="space-y-3 mt-2">
          <div className="space-y-1">
            <Label>Titre</Label>
            <Input {...form.register("title")} />
            {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Type</Label>
              <Select {...form.register("exam_type")}>
                <option value="practice">Entraînement</option>
                <option value="mock_official">Examen blanc</option>
                <option value="category_focus">Focus catégorie</option>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Difficulté</Label>
              <Select {...form.register("difficulty")}>
                <option value="easy">Facile</option>
                <option value="medium">Moyen</option>
                <option value="hard">Difficile</option>
                <option value="mixed">Mixte</option>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Nb questions</Label>
              <Input {...form.register("question_count")} type="number" min={1} max={100} />
              {errors.question_count && <p className="text-xs text-destructive">{errors.question_count.message}</p>}
            </div>
            <div className="space-y-1">
              <Label>Durée (secondes)</Label>
              <Input {...form.register("time_limit_seconds")} type="number" min={60} />
            </div>
            <div className="space-y-1">
              <Label>Score requis (%)</Label>
              <Input {...form.register("passing_score_percentage")} type="number" min={0} max={100} step={0.5} />
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
