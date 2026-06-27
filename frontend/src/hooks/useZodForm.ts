"use client";

import { useForm, type UseFormProps, type FieldValues } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { ZodType } from "zod";

/**
 * Hook partagé qui câble zodResolver automatiquement.
 * Évite la duplication de `resolver: zodResolver(schema)` dans chaque formulaire.
 *
 * Usage :
 *   const form = useZodForm({ schema: myZodSchema, defaultValues: { ... } });
 */
export function useZodForm<T extends FieldValues>({
  schema,
  ...formProps
}: UseFormProps<T> & { schema: ZodType<T> }) {
  return useForm<T>({
    ...formProps,
    resolver: zodResolver(schema),
  });
}
