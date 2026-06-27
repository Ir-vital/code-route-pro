"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    console.error("Global app error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-destructive/10">
        <AlertTriangle size={36} className="text-destructive" />
      </div>
      <div className="space-y-2">
        <h1 className="text-2xl font-bold">Une erreur est survenue</h1>
        <p className="text-muted-foreground max-w-md">
          {error.message || "Quelque chose s'est mal passé. Veuillez réessayer."}
        </p>
        {error.digest && (
          <p className="text-xs text-muted-foreground font-mono">ID : {error.digest}</p>
        )}
      </div>
      <button
        onClick={reset}
        className="rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        Réessayer
      </button>
    </div>
  );
}
