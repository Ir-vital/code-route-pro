-- =============================================================================
-- Seed : Badges de gamification
-- =============================================================================

INSERT INTO badges (id, name, description, icon, criteria_type, criteria_value)
VALUES
    -- Examens passés
    (gen_random_uuid(), 'Premier pas',     'Passer son premier examen',         '🎯', 'exam_count', 1),
    (gen_random_uuid(), 'Assidu',          'Passer 10 examens',                  '📚', 'exam_count', 10),
    (gen_random_uuid(), 'Persévérant',     'Passer 50 examens',                  '💪', 'exam_count', 50),
    (gen_random_uuid(), 'Expert',          'Passer 100 examens',                 '🏆', 'exam_count', 100),

    -- Score parfait
    (gen_random_uuid(), 'Parfait !',       'Obtenir 100% à un examen',           '⭐', 'perfect_score', 1),
    (gen_random_uuid(), 'Sans faute',      'Obtenir 100% à 5 examens',           '🌟', 'perfect_score', 5),

    -- Série quotidienne
    (gen_random_uuid(), 'Régulier',        'Pratiquer 7 jours de suite',         '🔥', 'streak', 7),
    (gen_random_uuid(), 'Habitué',         'Pratiquer 30 jours de suite',        '🔥🔥', 'streak', 30),

    -- Maîtrise catégorie
    (gen_random_uuid(), 'Maître Danger',   'Maîtriser les panneaux de danger',   '⚠️', 'category_mastery', 80),
    (gen_random_uuid(), 'Maître Règles',   'Maîtriser les interdictions',        '🚫', 'category_mastery', 80)
ON CONFLICT DO NOTHING;
