-- =============================================================================
-- Seed : Modèles d'examens
-- Nécessite que les catégories existent (seed 02).
-- =============================================================================

-- Examen blanc officiel (40 questions, 40 minutes)
INSERT INTO exams (id, title, description, exam_type, question_count, time_limit_seconds, passing_score_percentage, difficulty, is_active)
VALUES
    (
        gen_random_uuid(),
        'Examen blanc officiel',
        'Simulez les conditions réelles de l''examen du code de la route. 40 questions, 40 minutes, seuil de réussite à 35/40.',
        'mock_official',
        40,
        2400,
        87.50,
        'mixed',
        TRUE
    ),
    (
        gen_random_uuid(),
        'Entraînement libre — Facile',
        'Pratiquez avec des questions faciles pour consolider vos bases.',
        'practice',
        20,
        1200,
        80.00,
        'easy',
        TRUE
    ),
    (
        gen_random_uuid(),
        'Entraînement libre — Moyen',
        'Questions de difficulté intermédiaire.',
        'practice',
        20,
        1200,
        80.00,
        'medium',
        TRUE
    ),
    (
        gen_random_uuid(),
        'Entraînement libre — Difficile',
        'Questions difficiles pour les candidats avancés.',
        'practice',
        20,
        1200,
        80.00,
        'hard',
        TRUE
    )
ON CONFLICT DO NOTHING;

-- Examens par catégorie (category_focus)
-- Nécessite que les slugs des catégories existent
INSERT INTO exams (id, title, description, exam_type, category_id, question_count, time_limit_seconds, passing_score_percentage, difficulty, is_active)
SELECT
    gen_random_uuid(),
    'Focus : ' || c.name,
    'Entraînement ciblé sur la catégorie : ' || c.name,
    'category_focus',
    c.id,
    15,
    900,
    80.00,
    'mixed',
    TRUE
FROM categories c
WHERE c.is_active = TRUE
ON CONFLICT DO NOTHING;
