import type { Metadata } from "next";

import { ProfileView } from "@/features/auth/components/ProfileView";

export const metadata: Metadata = { title: "Mon profil" };

export default function ProfilePage() {
  return <ProfileView />;
}
