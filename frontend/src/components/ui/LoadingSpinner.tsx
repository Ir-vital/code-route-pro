import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizes = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-4",
};

export function LoadingSpinner({ size = "md", className }: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Chargement…"
      className={cn(
        "animate-spin rounded-full border-primary border-t-transparent",
        sizes[size],
        className
      )}
    />
  );
}

export function PageLoader() {
  return (
    <div className="flex h-64 w-full items-center justify-center">
      <LoadingSpinner size="lg" />
    </div>
  );
}
