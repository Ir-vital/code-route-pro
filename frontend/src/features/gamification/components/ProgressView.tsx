"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/axios-client";
import { BadgeCard } from "./BadgeCard";
import { LevelIndicator } from "./LevelIndicator";
import { StreakCounter } from "./StreakCounter";
import { CategoryMasteryRadar } from "./CategoryMasteryRadar";
import { AnimatedContainer } from "@/components/ui/AnimatedContainer";
import { PageLoader } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useCategories } from "@/features/learn/hooks/useLearn";

export function ProgressView() {
  const { data: progress, isLoading: loadingProgress } = useQuery({
    queryKey: ["user-progress"],
    queryFn: () => apiClient.get("/dashboard/summary").then((r) => r.data),
  });

  const { data: userBadges, isLoading: loadingBadges } = useQuery({
    queryKey: ["badges", "me"],
    queryFn: () => apiClient.get("/badges/me").then((r) => r.data) as Promise<any[]>,
  });

  const { data: badgeCatalog } = useQuery({
    queryKey: ["badges"],
    queryFn: () => apiClient.get("/badges").then((r) => r.data) as Promise<any[]>,
  });

  const { data: masteryData } = useQuery({
    queryKey: ["dashboard", "category-mastery"],
    queryFn: () => apiClient.get("/dashboard/category-mastery").then((r) => r.data) as Promise<any[]>,
  });

  const { data: categories } = useCategories();

  if (loadingProgress || loadingBadges) return <PageLoader />;

  // Construire les données radar
  const radarData = (masteryData ?? []).map((m: any) => {
    const cat = categories?.find((c) => c.id === m.category_id);
    return {
      category: cat?.name ?? m.category_id.slice(0, 8),
      mastery: parseFloat(m.mastery_percentage),
    };
  });

  // Map badges obtenus
  const earnedBadgeIds = new Set((userBadges ?? []).map((ub: any) => ub.badge.id));

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Ma progression</h1>

      {/* Niveau & Streak */}
      <AnimatedContainer>
        <div className="grid md:grid-cols-2 gap-4">
          {progress && (
            <LevelIndicator
              level={progress.level ?? 1}
              xpPoints={progress.xp_points ?? 0}
            />
          )}
          {progress && (
            <StreakCounter
              currentStreak={progress.current_streak_days ?? 0}
              longestStreak={0}
            />
          )}
        </div>
      </AnimatedContainer>

      {/* Radar maîtrise */}
      {radarData.length > 0 && (
        <AnimatedContainer delay={0.1}>
          <CategoryMasteryRadar data={radarData} />
        </AnimatedContainer>
      )}

      {/* Badges obtenus */}
      <AnimatedContainer delay={0.15}>
        <section>
          <h2 className="text-xl font-semibold mb-4">
            Mes badges ({userBadges?.length ?? 0})
          </h2>
          {!userBadges?.length ? (
            <EmptyState
              title="Aucun badge encore"
              description="Passez des examens pour débloquer vos premiers badges !"
            />
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(userBadges ?? []).map((ub: any) => (
                <BadgeCard
                  key={ub.badge.id}
                  name={ub.badge.name}
                  description={ub.badge.description}
                  icon={ub.badge.icon}
                  earned
                  earnedAt={ub.earned_at}
                />
              ))}
            </div>
          )}
        </section>
      </AnimatedContainer>

      {/* Catalogue complet */}
      <AnimatedContainer delay={0.2}>
        <section>
          <h2 className="text-xl font-semibold mb-4">Badges à débloquer</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {(badgeCatalog ?? [])
              .filter((b: any) => !earnedBadgeIds.has(b.id))
              .map((b: any) => (
                <BadgeCard
                  key={b.id}
                  name={b.name}
                  description={b.description}
                  icon={b.icon}
                  earned={false}
                />
              ))}
          </div>
        </section>
      </AnimatedContainer>
    </div>
  );
}
