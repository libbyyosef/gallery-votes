# server/tests/conftest.py
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# ---------------------- ADMIN URL (to create/drop test DB) ----------------------
def _build_admin_url():
    raw = os.getenv("TEST_DB_ADMIN_URL")
    if raw:
        sanitized = (
            raw.replace(":PORT", ":5432")
               .replace(":${PORT}", ":5432")
               .replace(":<PORT>", ":5432")
        )
        try:
            return make_url(sanitized)
        except Exception:
            pass
    host = os.getenv("TEST_DB_HOST", "localhost")
    port = int(os.getenv("TEST_DB_PORT", "5432"))
    user = os.getenv("TEST_DB_USER", "app")
    password = os.getenv("TEST_DB_PASSWORD", "app")
    return make_url(f"postgresql+psycopg://{user}:{password}@{host}:{port}/postgres")

ADMIN_URL = _build_admin_url()
TEST_DB_NAME = f"app_test_{uuid4().hex[:8]}"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql_db" / "schema.sql"

# Point app's DATABASE_URL to the ephemeral DB (plain driver; your app upgrades to +psycopg)
_test_url_sqlalchemy = ADMIN_URL.set(database=TEST_DB_NAME)
_plain_for_env = _test_url_sqlalchemy.set(drivername="postgresql")
os.environ["DATABASE_URL"] = str(_plain_for_env)

# Import app/db *after* DATABASE_URL is set
from server.main import app  # noqa: E402
from server.db import db as dbmod  # noqa: E402


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create an ephemeral test database in AUTOCOMMIT, yield engine bound to it, drop after.
    """
    admin_engine = create_engine(ADMIN_URL, pool_pre_ping=True, future=True)

    # --- CREATE DATABASE (must be autocommit) ---
    with admin_engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.exec_driver_sql(f'CREATE DATABASE "{TEST_DB_NAME}"')

    # Engine bound to the new DB
    engine = create_engine(_test_url_sqlalchemy, pool_pre_ping=True, future=True)

    try:
        yield engine
    finally:
        engine.dispose()
        # Terminate connections & DROP DATABASE in AUTOCOMMIT
        with admin_engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(
                text("""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :dbname AND pid <> pg_backend_pid()
                """),
                {"dbname": TEST_DB_NAME},
            )
            conn.exec_driver_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
        admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def apply_schema_once(test_db_engine):
    """
    Apply schema to the ephemeral DB once per session and ensure we're on the test DB.
    """
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"schema.sql not found at: {SCHEMA_PATH}")

    with test_db_engine.begin() as conn:
        currdb = conn.execute(text("select current_database()")).scalar_one()
        assert currdb.startswith("app_test_"), f"Refusing to run tests on '{currdb}'"

        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.exec_driver_sql(sql)
        conn.exec_driver_sql("TRUNCATE TABLE public.images RESTART IDENTITY CASCADE;")

    # Belt & suspenders: make app's engine/session use the test engine
    dbmod.engine.dispose(close=False)
    dbmod.engine = test_db_engine
    dbmod.SessionLocal = sessionmaker(
        bind=test_db_engine, autoflush=False, autocommit=False, future=True
    )


@pytest.fixture()
def db_session(test_db_engine):
    """
    Each test runs inside a transaction on the test DB and rolls back afterwards.
    """
    connection = test_db_engine.connect()
    trans = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    """
    FastAPI TestClient that uses the transactional session (never the real DB).
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[dbmod.get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_images(db_session):
    """
    Insert a few rows for tests (rolled back after each test).
    """
    db_session.execute(
        text("INSERT INTO public.images (picsum_id) VALUES (:pid)"),
        [{"pid": "101"}, {"pid": "102"}, {"pid": "103"}],
    )
    db_session.commit()
    ids = db_session.execute(text("SELECT image_id FROM public.images ORDER BY image_id")).scalars().all()
    return ids
