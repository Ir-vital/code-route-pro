import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Requis pour le Dockerfile multi-stage (node server.js)
  output: "standalone",

  // Optimisation des images depuis Supabase Storage
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.supabase.co",
        pathname: "/storage/v1/object/public/**",
      },
    ],
  },

  // Variables d'environnement exposées côté client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
