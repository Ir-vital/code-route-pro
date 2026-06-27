import type { Metadata } from "next";

import { ResetPasswordForm } from "@/features/auth/components/ResetPasswordForm";

export const metadata: Metadata = { title: "Réinitialiser le mot de passe" };

export default function ResetPasswordPage() {
  return <ResetPasswordForm />;
}
