import os
from urllib.parse import urlparse, unquote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

RAW_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")

def _as_sqlalchemy_url(raw: str) -> str | URL:
    if raw.startswith("postgresql+"):
        return raw

    u = urlparse(raw)
    return URL.create(
        drivername="postgresql+psycopg",              # psycopg3
        username=unquote(u.username) if u.username else None,
        password=unquote(u.password) if u.password else None,
        host=u.hostname or "localhost",
        port=u.port or 5432,
        database=(u.path.lstrip("/") or "postgres"),
        query={}, 
    )

SQLALCHEMY_URL = _as_sqlalchemy_url(RAW_URL)

engine = create_engine(SQLALCHEMY_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
