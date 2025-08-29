import pytest
from sqlalchemy import text
from server.db.db import engine, SessionLocal

class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    def test_database_connection(self):
        """Test that database connection works"""
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    def test_session_creation(self):
        """Test that database session can be created"""
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1")).scalar()
            assert result == 1
        finally:
            db.close()
    
    def test_transaction_rollback(self, db_session):
        """Test that transactions can be rolled back"""
        from server.models.image_model import ImageModel
        
        image = ImageModel(picsum_id="test-rollback")
        db_session.add(image)
        
        # Rollback
        db_session.rollback()
        
        result = db_session.execute(
            text("SELECT COUNT(*) FROM images WHERE picsum_id = 'test-rollback'")
        ).scalar()
        assert result == 0