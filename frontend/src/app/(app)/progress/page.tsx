import type { Metadata } from "next";

import { ProgressView } from "@/features/gamification/components/ProgressView";

export const metadata: Metadata = { title: "Ma progression" };

export default function ProgressPage() {
  return <ProgressView />;
}
