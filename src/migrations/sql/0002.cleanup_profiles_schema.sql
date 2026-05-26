-- depends: 0001.create_profiles_table
DO $$
DECLARE
    col RECORD;
BEGIN
    FOR col IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'profiles'
          AND column_name NOT IN (
              'id',
              'user_id',
              'username',
              'email',
              'first_name',
              'last_name',
              'bio',
              'created_at',
              'updated_at'
          )
    LOOP
        EXECUTE format('ALTER TABLE profiles DROP COLUMN %I', col.column_name);
    END LOOP;
END $$;
