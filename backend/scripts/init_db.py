#!/usr/bin/env python3
"""Initialize PostgreSQL tables from SQLAlchemy models + optional schema.sql."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database.connection import Base, engine
from app.database import models  # noqa: F401


def main():
    print("Creating tables via SQLAlchemy...")
    Base.metadata.create_all(bind=engine)

    schema_path = Path(__file__).resolve().parent.parent.parent / "database" / "schema.sql"
    if schema_path.exists():
        print("Applying views from schema.sql...")
        sql = schema_path.read_text()
        # Run view/compat statements only (tables already created by ORM)
        view_stmts = [s.strip() for s in sql.split(";") if "CREATE OR REPLACE VIEW" in s.upper()]
        with engine.connect() as conn:
            for stmt in view_stmts:
                if stmt:
                    try:
                        conn.execute(text(stmt))
                    except Exception as e:
                        print(f"  skip: {e}")
            conn.commit()
    print("Database initialized.")


if __name__ == "__main__":
    main()
