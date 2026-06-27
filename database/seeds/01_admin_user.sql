-- =============================================================================
-- Seed : Utilisateur administrateur par défaut
-- Mot de passe : Admin1234  (bcrypt hash — à changer immédiatement en prod)
-- =============================================================================

INSERT INTO users (
    id, email, hashed_password, first_name, last_name, role, is_active, is_verified
)
VALUES (
    gen_random_uuid(),
    'admin@codeRoutepro.fr',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3AXi/8cGjW', -- Admin1234
    'Super',
    'Admin',
    'admin',
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;
