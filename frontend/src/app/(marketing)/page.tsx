import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-3xl text-center space-y-6">
        <h1 className="text-5xl font-bold text-primary">CodeRoute Pro</h1>
        <p className="text-xl text-muted-foreground">
          Préparez votre code de la route avec des examens blancs, des panneaux
          interactifs et un suivi de progression personnalisé.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/register"
            className="rounded-lg bg-primary px-6 py-3 text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            Commencer gratuitement
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-input px-6 py-3 font-medium hover:bg-accent transition-colors"
          >
            Se connecter
          </Link>
        </div>
      </div>
    </main>
  );
}
