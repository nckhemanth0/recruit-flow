from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = :table_name
            AND column_name = :column_name
        )
    """), {"table_name": table_name, "column_name": column_name})
    return result.scalar()


def add_column_if_not_exists(conn, table_name: str, column_name: str, column_type: str, nullable: bool = False, default_value: str = None):
    """Add a column to a table if it doesn't exist."""
    if not column_exists(conn, table_name, column_name):
        # For NOT NULL columns in existing tables, we need to add with a default or allow NULL first
        if nullable:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
        elif default_value is not None:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value} NOT NULL;"
        else:
            # For non-nullable without default, add as nullable first (we'll handle updates separately if needed)
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
        conn.execute(text(sql))
        print(f"✓ Added '{column_name}' column to '{table_name}' table")
        return True
    else:
        print(f"ℹ '{column_name}' column already exists in '{table_name}' table")
        return False


def add_missing_columns():
    """Add all missing columns from all models."""
    with engine.begin() as conn:
        print("Checking and adding missing columns...")
        
        # Jobs table columns
        add_column_if_not_exists(conn, "jobs", "company", "VARCHAR(255)", nullable=False, default_value="''")
        add_column_if_not_exists(conn, "jobs", "location", "VARCHAR(255)", nullable=False, default_value="''")
        add_column_if_not_exists(conn, "jobs", "department", "VARCHAR(255)", nullable=True)
        add_column_if_not_exists(conn, "jobs", "employment_type", "VARCHAR(100)", nullable=False, default_value="'Full-time'")
        add_column_if_not_exists(conn, "jobs", "status", "VARCHAR(50)", nullable=False, default_value="'open'")
        add_column_if_not_exists(conn, "jobs", "description", "TEXT", nullable=False, default_value="''")
        add_column_if_not_exists(conn, "jobs", "requirements", "TEXT", nullable=True)
        add_column_if_not_exists(conn, "jobs", "min_salary", "NUMERIC(10, 2)", nullable=True)
        add_column_if_not_exists(conn, "jobs", "max_salary", "NUMERIC(10, 2)", nullable=True)
        add_column_if_not_exists(conn, "jobs", "created_by_id", "INTEGER", nullable=True)
        add_column_if_not_exists(conn, "jobs", "created_at", "TIMESTAMP", nullable=False, default_value="CURRENT_TIMESTAMP")
        
        # Users table columns
        add_column_if_not_exists(conn, "users", "phone", "VARCHAR(50)", nullable=True)
        add_column_if_not_exists(conn, "users", "location", "VARCHAR(255)", nullable=True)
        add_column_if_not_exists(conn, "users", "bio", "TEXT", nullable=True)
        add_column_if_not_exists(conn, "users", "full_name", "VARCHAR(255)", nullable=True)
        add_column_if_not_exists(conn, "users", "role", "VARCHAR(50)", nullable=False, default_value="'candidate'")
        add_column_if_not_exists(conn, "users", "created_at", "TIMESTAMP", nullable=False, default_value="CURRENT_TIMESTAMP")
        
        # Applications table columns
        add_column_if_not_exists(conn, "applications", "stage_id", "INTEGER", nullable=True)
        add_column_if_not_exists(conn, "applications", "status", "VARCHAR(50)", nullable=False, default_value="'active'")
        add_column_if_not_exists(conn, "applications", "resume_path", "VARCHAR(500)", nullable=True)
        add_column_if_not_exists(conn, "applications", "cover_letter", "TEXT", nullable=True)
        add_column_if_not_exists(conn, "applications", "created_at", "TIMESTAMP", nullable=False, default_value="CURRENT_TIMESTAMP")
        add_column_if_not_exists(conn, "applications", "updated_at", "TIMESTAMP", nullable=False, default_value="CURRENT_TIMESTAMP")
        
        # Job stages table columns (if table exists)
        if column_exists(conn, "job_stages", "id"):  # Check if table exists
            add_column_if_not_exists(conn, "job_stages", "position", "INTEGER", nullable=False, default_value="0")
        
        # Application notes table columns (if table exists)
        if column_exists(conn, "application_notes", "id"):  # Check if table exists
            add_column_if_not_exists(conn, "application_notes", "author_id", "INTEGER", nullable=True)
            add_column_if_not_exists(conn, "application_notes", "created_at", "TIMESTAMP", nullable=False, default_value="CURRENT_TIMESTAMP")
        
        print("✓ Column migration check completed!")
