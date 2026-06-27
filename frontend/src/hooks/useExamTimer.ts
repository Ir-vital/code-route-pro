"use client";

import { useEffect, useRef } from "react";
import { useExamStore } from "@/stores/exam.store";

/**
 * Décrémente le timer d'examen chaque seconde.
 * Appelle onTimeUp() quand le temps arrive à 0.
 */
export function useExamTimer(onTimeUp: () => void) {
  const { timeRemainingSeconds, tick } = useExamStore();
  const onTimeUpRef = useRef(onTimeUp);
  onTimeUpRef.current = onTimeUp;

  useEffect(() => {
    if (timeRemainingSeconds <= 0) return;

    const interval = setInterval(() => {
      tick();
    }, 1000);

    return () => clearInterval(interval);
  }, [tick, timeRemainingSeconds]);

  useEffect(() => {
    if (timeRemainingSeconds === 0) {
      onTimeUpRef.current();
    }
  }, [timeRemainingSeconds]);

  const minutes = Math.floor(timeRemainingSeconds / 60);
  const seconds = timeRemainingSeconds % 60;
  const isWarning = timeRemainingSeconds <= 60;

  return {
    timeRemainingSeconds,
    formatted: `${minutes}:${seconds.toString().padStart(2, "0")}`,
    isWarning,
  };
}
