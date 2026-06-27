"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex flex-col items-center justify-center rounded-xl border border-destructive/30 bg-destructive/10 p-8 text-center">
          <AlertTriangle size={36} className="text-destructive mb-3" />
          <h3 className="text-lg font-semibold">Quelque chose s'est mal passé</h3>
          <p className="text-sm text-muted-foreground mt-1 max-w-sm">
            {this.state.error?.message ?? "Une erreur inattendue est survenue."}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
          >
            Réessayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
