from pathlib import Path


_MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "src" / "migrations" / "sql"


def test_profile_migrations_exist():
    assert (_MIGRATIONS_DIR / "0001.create_profiles_table.sql").is_file()
    assert (_MIGRATIONS_DIR / "0002.cleanup_profiles_schema.sql").is_file()


def test_profile_migrations_sql_has_no_avatar_reference():
    sql_files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
    combined = "\n".join(path.read_text() for path in sql_files).lower()
    assert "avatar" not in combined
