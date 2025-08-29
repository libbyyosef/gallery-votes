# server/tests/conftest.py
import os
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from server.main import app
from server.db.db import _as_sqlalchemy_url, get_db

RAW_URL = os.getenv("DATABASE_URL_TEST") or os.getenv(
    "DATABASE_URL", "postgresql://app:app@localhost:5432/app"
)
SQLALCHEMY_URL = _as_sqlalchemy_url(RAW_URL)
ENGINE = create_engine(SQLALCHEMY_URL, pool_pre_ping=True, future=True)

# tests are inside server/, so schema is one level up from tests/
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql_db" / "schema.sql"

@pytest.fixture(scope="session", autouse=True)
def apply_schema_once():
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"schema.sql not found at: {SCHEMA_PATH}")
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with ENGINE.begin() as conn:
        conn.exec_driver_sql(sql)
        conn.exec_driver_sql("TRUNCATE TABLE public.images RESTART IDENTITY CASCADE;")

@pytest.fixture()
def db_session():
    connection = ENGINE.connect()
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
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture()
def seed_images(db_session):
    db_session.execute(
        text("INSERT INTO public.images (picsum_id) VALUES (:pid)"),
        [{"pid": "101"}, {"pid": "102"}, {"pid": "103"}],
    )
    db_session.commit()
    ids = db_session.execute(text("SELECT image_id FROM public.images ORDER BY image_id")).scalars().all()
    return ids
