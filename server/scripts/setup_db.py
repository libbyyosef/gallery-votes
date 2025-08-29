from pathlib import Path
from server.db.db import engine
from server.scripts.seed_images import main as seed_main

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql_db" / "schema.sql"

def apply_schema() -> None:
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"schema.sql not found at: {SCHEMA_PATH}")
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
    print(f" Applied schema: {SCHEMA_PATH}")

if __name__ == "__main__":
    apply_schema()
    seed_main()
    print("DB setup complete (schema + 100 images).")
