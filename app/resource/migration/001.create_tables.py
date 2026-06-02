from yoyo import step

__depends__ = {}

steps = [
    # Set the time zone for consistent timestamp handling
    step("SET TIME ZONE 'America/Mexico_City';", ignore_errors='apply'),

    # Define the function to update timestamps
    step("""
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """, ignore_errors='apply'),


    # Create merged Usuarios table (combining user_registrations + Usuarios)
    step("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(100) NOT NULL DEFAULT '',
            email VARCHAR(255),
            full_name VARCHAR(255),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            profile JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """),

    # Add trigger for users table
    step("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgname = 'update_users_updated_at'
            ) THEN
                CREATE TRIGGER update_users_updated_at
                BEFORE UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            END IF;
        END $$;
    """),
    step(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND indexname = 'users_email_key'
            ) THEN
                CREATE UNIQUE INDEX users_email_key ON users (email) WHERE email IS NOT NULL;
            END IF;
        END $$;
        """
    ),
]
