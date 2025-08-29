import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.db.db import get_db
from server.models.base import Base
from server.models.image_model import ImageModel
from server.main import app

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_images(db_session):
    """Create sample images for testing"""
    images = [
        ImageModel(picsum_id="237", label="Test Image 1", like_count=5, dislike_count=2),
        ImageModel(picsum_id="238", label="Test Image 2", like_count=0, dislike_count=0),
        ImageModel(picsum_id="239", label="Test Image 3", like_count=10, dislike_count=1),
    ]
    db_session.add_all(images)
    db_session.commit()
    
    # Refresh to get auto-generated image_ids
    for img in images:
        db_session.refresh(img)
    
    return images
