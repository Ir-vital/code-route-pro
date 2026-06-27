-- =============================================================================
-- Seed : Catégories de panneaux (code de la route français)
-- =============================================================================

INSERT INTO categories (id, name, slug, description, icon, color, display_order, is_active)
VALUES
    (gen_random_uuid(), 'Panneaux de danger',         'danger',         'Signalent un danger sur la route',         '⚠️',  '#FF6B35', 1,  TRUE),
    (gen_random_uuid(), 'Panneaux d''interdiction',   'interdiction',   'Interdisent certaines manœuvres',          '🚫',  '#E63946', 2,  TRUE),
    (gen_random_uuid(), 'Panneaux d''obligation',     'obligation',     'Imposent des comportements obligatoires',  '🔵',  '#457B9D', 3,  TRUE),
    (gen_random_uuid(), 'Panneaux d''indication',     'indication',     'Fournissent des informations utiles',      'ℹ️',  '#2A9D8F', 4,  TRUE),
    (gen_random_uuid(), 'Panneaux de direction',      'direction',      'Indiquent les directions et distances',    '🗺️',  '#264653', 5,  TRUE),
    (gen_random_uuid(), 'Panneaux de prescription',   'prescription',   'Précisent des règles de circulation',      '📋',  '#8338EC', 6,  TRUE),
    (gen_random_uuid(), 'Feux de signalisation',      'feux',           'Règles liées aux feux tricolores',         '🚦',  '#FB8500', 7,  TRUE),
    (gen_random_uuid(), 'Marquages au sol',           'marquages',      'Lignes et marquages sur la chaussée',      '🛣️',  '#023047', 8,  TRUE)
ON CONFLICT (slug) DO NOTHING;
