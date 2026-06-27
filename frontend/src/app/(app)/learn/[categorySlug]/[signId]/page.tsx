import type { Metadata } from "next";

import { SignDetailPanel } from "@/features/learn/components/SignDetailPanel";

interface Props {
  params: Promise<{ categorySlug: string; signId: string }>;
}

export const metadata: Metadata = { title: "Détail du panneau" };

export default async function SignDetailPage({ params }: Props) {
  const { signId } = await params;
  return <SignDetailPanel signId={signId} />;
}
