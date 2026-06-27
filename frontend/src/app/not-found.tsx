import Link from "next/link";
import { FileQuestion } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
        <FileQuestion size={36} className="text-muted-foreground" />
      </div>
      <div className="space-y-2">
        <h1 className="text-4xl font-bold">404</h1>
        <p className="text-lg text-muted-foreground">Cette page n'existe pas.</p>
      </div>
      <div className="flex gap-3">
        <Link
          href="/dashboard"
          className="rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Retour au tableau de bord
        </Link>
        <Link
          href="/"
          className="rounded-md border px-5 py-2.5 text-sm font-medium hover:bg-accent transition-colors"
        >
          Accueil
        </Link>
      </div>
    </div>
  );
}
