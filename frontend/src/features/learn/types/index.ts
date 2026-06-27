export type Difficulty = "easy" | "medium" | "hard";

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  display_order: number;
  is_active: boolean;
}

export interface Sign {
  id: string;
  category_id: string;
  name: string;
  official_code: string | null;
  image_url: string;
  meaning: string;
  rules: string | null;
  difficulty: Difficulty;
  is_active: boolean;
}

export interface Favorite {
  id: string;
  sign_id: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
