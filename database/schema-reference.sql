-- =============================================================================
-- CodeRoute Pro — Schéma de référence PostgreSQL
-- Ce fichier est documentaire uniquement. La source de vérité sont les
-- migrations Alembic dans backend/alembic/versions/.
-- Généré manuellement à partir des modèles SQLAlchemy.
-- =============================================================================

-- ─── Extensions ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Énumérations ─────────────────────────────────────────────────────────────
CREATE TYPE user_role_enum AS ENUM ('admin', 'student');
CREATE TYPE difficulty_enum AS ENUM ('easy', 'medium', 'hard', 'mixed');
CREATE TYPE exam_type_enum AS ENUM ('practice', 'mock_official', 'category_focus');
CREATE TYPE attempt_status_enum AS ENUM ('in_progress', 'completed', 'abandoned');
CREATE TYPE question_type_enum AS ENUM ('single_choice', 'multiple_choice');
CREATE TYPE badge_criteria_type_enum AS ENUM ('exam_count', 'perfect_score', 'streak', 'category_mastery');
CREATE TYPE notification_type_enum AS ENUM ('exam_result', 'new_exam_available', 'progress_update', 'badge_earned', 'system');

-- ─── users ────────────────────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    avatar_url      VARCHAR(500),
    role            user_role_enum NOT NULL DEFAULT 'student',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_role ON users (role);

-- ─── refresh_tokens ───────────────────────────────────────────────────────────
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked_at  TIMESTAMPTZ,
    user_agent  VARCHAR(500),
    ip_address  VARCHAR(45),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens (token_hash);

-- ─── password_reset_tokens ────────────────────────────────────────────────────
CREATE TABLE password_reset_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_prt_user_id ON password_reset_tokens (user_id);

-- ─── categories ───────────────────────────────────────────────────────────────
CREATE TABLE categories (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(150) NOT NULL,
    slug          VARCHAR(160) NOT NULL UNIQUE,
    description   TEXT,
    icon          VARCHAR(100),
    color         VARCHAR(20),
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_categories_slug ON categories (slug);

-- ─── signs ────────────────────────────────────────────────────────────────────
CREATE TABLE signs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id   UUID NOT NULL REFERENCES categories (id) ON DELETE RESTRICT,
    name          VARCHAR(200) NOT NULL,
    official_code VARCHAR(50),
    image_url     VARCHAR(500) NOT NULL,
    meaning       TEXT NOT NULL,
    rules         TEXT,
    difficulty    difficulty_enum NOT NULL DEFAULT 'easy',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_signs_category_id ON signs (category_id);
CREATE INDEX idx_signs_official_code ON signs (official_code);

-- ─── favorites ────────────────────────────────────────────────────────────────
CREATE TABLE favorites (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    sign_id    UUID NOT NULL REFERENCES signs (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_favorites_user_sign UNIQUE (user_id, sign_id)
);
CREATE INDEX idx_favorites_user_id ON favorites (user_id);

-- ─── questions ────────────────────────────────────────────────────────────────
CREATE TABLE questions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id   UUID NOT NULL REFERENCES categories (id) ON DELETE RESTRICT,
    sign_id       UUID REFERENCES signs (id) ON DELETE SET NULL,
    content       TEXT NOT NULL,
    image_url     VARCHAR(500),
    explanation   TEXT,
    question_type question_type_enum NOT NULL DEFAULT 'single_choice',
    difficulty    difficulty_enum NOT NULL DEFAULT 'easy',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_questions_category_id ON questions (category_id);

-- ─── question_options ─────────────────────────────────────────────────────────
CREATE TABLE question_options (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id   UUID NOT NULL REFERENCES questions (id) ON DELETE CASCADE,
    content       VARCHAR(500) NOT NULL,
    is_correct    BOOLEAN NOT NULL DEFAULT FALSE,
    display_order INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_question_options_question_id ON question_options (question_id);

-- ─── exams ────────────────────────────────────────────────────────────────────
CREATE TABLE exams (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title                    VARCHAR(200) NOT NULL,
    description              TEXT,
    exam_type                exam_type_enum NOT NULL,
    category_id              UUID REFERENCES categories (id) ON DELETE SET NULL,
    question_count           INTEGER NOT NULL,
    time_limit_seconds       INTEGER NOT NULL,
    passing_score_percentage NUMERIC(5, 2) NOT NULL DEFAULT 80.00,
    difficulty               difficulty_enum NOT NULL DEFAULT 'mixed',
    is_active                BOOLEAN NOT NULL DEFAULT TRUE,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── exam_attempts ────────────────────────────────────────────────────────────
CREATE TABLE exam_attempts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    exam_id          UUID NOT NULL REFERENCES exams (id) ON DELETE RESTRICT,
    status           attempt_status_enum NOT NULL DEFAULT 'in_progress',
    started_at       TIMESTAMPTZ NOT NULL,
    finished_at      TIMESTAMPTZ,
    duration_seconds INTEGER,
    score_percentage NUMERIC(5, 2),
    is_passed        BOOLEAN,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_exam_attempts_user_id ON exam_attempts (user_id);
CREATE INDEX idx_exam_attempts_exam_id ON exam_attempts (exam_id);
CREATE INDEX idx_exam_attempts_status ON exam_attempts (status);

-- ─── attempt_questions ────────────────────────────────────────────────────────
CREATE TABLE attempt_questions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id    UUID NOT NULL REFERENCES exam_attempts (id) ON DELETE CASCADE,
    question_id   UUID NOT NULL REFERENCES questions (id) ON DELETE RESTRICT,
    display_order INTEGER NOT NULL
);
CREATE INDEX idx_attempt_questions_attempt_id ON attempt_questions (attempt_id);

-- ─── attempt_answers ──────────────────────────────────────────────────────────
CREATE TABLE attempt_answers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id  UUID NOT NULL REFERENCES exam_attempts (id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions (id) ON DELETE RESTRICT,
    is_correct  BOOLEAN,
    answered_at TIMESTAMPTZ
);
CREATE INDEX idx_attempt_answers_attempt_id ON attempt_answers (attempt_id);

-- ─── attempt_answer_options ───────────────────────────────────────────────────
CREATE TABLE attempt_answer_options (
    attempt_answer_id  UUID NOT NULL REFERENCES attempt_answers (id) ON DELETE CASCADE,
    question_option_id UUID NOT NULL REFERENCES question_options (id) ON DELETE RESTRICT,
    PRIMARY KEY (attempt_answer_id, question_option_id)
);

-- ─── badges ───────────────────────────────────────────────────────────────────
CREATE TABLE badges (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(150) NOT NULL,
    description     TEXT,
    icon            VARCHAR(100),
    criteria_type   badge_criteria_type_enum NOT NULL,
    criteria_value  INTEGER NOT NULL
);

-- ─── user_badges ──────────────────────────────────────────────────────────────
CREATE TABLE user_badges (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id   UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    badge_id  UUID NOT NULL REFERENCES badges (id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_user_badges_user_badge UNIQUE (user_id, badge_id)
);
CREATE INDEX idx_user_badges_user_id ON user_badges (user_id);

-- ─── user_progress ────────────────────────────────────────────────────────────
CREATE TABLE user_progress (
    user_id              UUID PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    level                INTEGER NOT NULL DEFAULT 1,
    xp_points            INTEGER NOT NULL DEFAULT 0,
    current_streak_days  INTEGER NOT NULL DEFAULT 0,
    longest_streak_days  INTEGER NOT NULL DEFAULT 0,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── category_mastery ─────────────────────────────────────────────────────────
CREATE TABLE category_mastery (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    category_id        UUID NOT NULL REFERENCES categories (id) ON DELETE CASCADE,
    mastery_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    last_practiced_at  TIMESTAMPTZ,
    CONSTRAINT uq_category_mastery_user_cat UNIQUE (user_id, category_id)
);
CREATE INDEX idx_category_mastery_user_id ON category_mastery (user_id);

-- ─── recommendations ──────────────────────────────────────────────────────────
CREATE TABLE recommendations (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    category_id  UUID NOT NULL REFERENCES categories (id) ON DELETE CASCADE,
    reason       VARCHAR(255),
    priority     INTEGER NOT NULL DEFAULT 0,
    generated_at TIMESTAMPTZ NOT NULL,
    is_dismissed BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_recommendations_user_id ON recommendations (user_id);

-- ─── notifications ────────────────────────────────────────────────────────────
CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    type       notification_type_enum NOT NULL,
    title      VARCHAR(200) NOT NULL,
    message    TEXT NOT NULL,
    payload    JSONB,
    is_read    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user_id ON notifications (user_id);
CREATE INDEX idx_notifications_is_read ON notifications (user_id, is_read);

-- ─── audit_logs ───────────────────────────────────────────────────────────────
CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id    UUID REFERENCES users (id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id   UUID,
    metadata    JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_logs_actor_id ON audit_logs (actor_id);
CREATE INDEX idx_audit_logs_action ON audit_logs (action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs (created_at DESC);

-- ─── Trigger updated_at automatique ──────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_signs_updated_at BEFORE UPDATE ON signs FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_questions_updated_at BEFORE UPDATE ON questions FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_exams_updated_at BEFORE UPDATE ON exams FOR EACH ROW EXECUTE FUNCTION update_updated_at();
