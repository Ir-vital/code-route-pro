"use client";

import { motion, type HTMLMotionProps } from "framer-motion";

interface AnimatedContainerProps extends HTMLMotionProps<"div"> {
  delay?: number;
  children: React.ReactNode;
}

/** Wrapper Framer Motion avec animation fade-in + slide-up par défaut. */
export function AnimatedContainer({
  children,
  delay = 0,
  ...props
}: AnimatedContainerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25, delay, ease: "easeOut" }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/** Variante pour les listes — chaque enfant s'anime en cascade. */
export function AnimatedList({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        visible: { transition: { staggerChildren: 0.06 } },
        hidden: {},
      }}
    >
      {children}
    </motion.div>
  );
}

export function AnimatedListItem({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      variants={{
        hidden: { opacity: 0, y: 10 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.2 } },
      }}
    >
      {children}
    </motion.div>
  );
}
