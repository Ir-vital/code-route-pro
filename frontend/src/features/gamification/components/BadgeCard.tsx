import { cn } from "@/lib/utils";

interface BadgeCardProps {
  name: string;
  description?: string | null;
  icon?: string | null;
  earned?: boolean;
  earnedAt?: string | null;
}

export function BadgeCard({ name, description, icon, earned = false, earnedAt }: BadgeCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center gap-2 rounded-xl border p-4 text-center transition-all",
        earned
          ? "border-primary/30 bg-primary/5 shadow-sm"
          : "border-dashed bg-muted/30 opacity-50 grayscale"
      )}
    >
      {icon ? (
        <span className="text-4xl" role="img" aria-label={name}>{icon}</span>
      ) : (
        <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center text-xl">🏅</div>
      )}
      <p className="text-sm font-semibold leading-tight">{name}</p>
      {description && (
        <p className="text-xs text-muted-foreground leading-tight">{description}</p>
      )}
      {earned && earnedAt && (
        <p className="text-xs text-primary font-medium">
          Obtenu le {new Date(earnedAt).toLocaleDateString("fr-FR")}
        </p>
      )}
    </div>
  );
}
