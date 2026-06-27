"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface MasteryData {
  category: string;
  mastery: number;
}

interface CategoryMasteryRadarProps {
  data: MasteryData[];
}

export function CategoryMasteryRadar({ data }: CategoryMasteryRadarProps) {
  if (!data.length) return null;

  return (
    <div className="rounded-xl border bg-card p-6">
      <h2 className="font-semibold mb-4">Maîtrise par catégorie</h2>
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="hsl(var(--border))" />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          />
          <Radar
            name="Maîtrise"
            dataKey="mastery"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.25}
            strokeWidth={2}
          />
          <Tooltip
            formatter={(v: number) => [`${v.toFixed(1)}%`, "Maîtrise"]}
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
