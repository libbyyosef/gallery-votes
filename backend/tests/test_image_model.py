import pytest
from server.models.image_model import ImageModel

class TestImageModelProperties:
    """Test ImageModel computed properties"""
    
    def test_source_url_property(self, db_session):
        """Test source_url computed property"""
        image = ImageModel(picsum_id="237")
        db_session.add(image)
        db_session.commit()
        
        expected_url = "https://picsum.photos/id/237/600/400.webp"
        assert image.source_url == expected_url
    
    def test_source_url_different_id(self, db_session):
        """Test source_url with different picsum_id"""
        image = ImageModel(picsum_id="100")
        db_session.add(image)
        db_session.commit()
        
        expected_url = "https://picsum.photos/id/100/600/400.webp"
        assert image.source_url == expected_url
    
    def test_likes_property(self, db_session):
        """Test likes computed property"""
        image = ImageModel(picsum_id="237", like_count=5)
        db_session.add(image)
        db_session.commit()
        
        assert image.likes == 5
    
    def test_likes_property_none(self, db_session):
        """Test likes property handles None"""
        image = ImageModel(picsum_id="237", like_count=None)
        db_session.add(image)
        db_session.commit()
        
        assert image.likes == 0
    
    def test_dislikes_property(self, db_session):
        """Test dislikes computed property"""
        image = ImageModel(picsum_id="237", dislike_count=3)
        db_session.add(image)
        db_session.commit()
        
        assert image.dislikes == 3
    
    def test_dislikes_property_none(self, db_session):
        """Test dislikes property handles None"""
        image = ImageModel(picsum_id="237", dislike_count=None)
        db_session.add(image)
        db_session.commit()
        
        assert image.dislikes == 0
    
    def test_is_liked_property(self, db_session):
        """Test is_liked property (always False)"""
        image = ImageModel(picsum_id="237")
        db_session.add(image)
        db_session.commit()
        
        assert image.is_liked is False
    
    def test_is_disliked_property(self, db_session):
        """Test is_disliked property (always False)"""
        image = ImageModel(picsum_id="237")
        db_session.add(image)
        db_session.commit()
        
        assert image.is_disliked is False

class TestImageModelCreation:
    """Test ImageModel database operations"""
    
    def test_create_image_with_defaults(self, db_session):
        """Test creating image with default values"""
        image = ImageModel(picsum_id="237")
        db_session.add(image)
        db_session.commit()
        db_session.refresh(image)
        
        assert image.image_id is not None
        assert image.picsum_id == "237"
        assert image.like_count == 0
        assert image.dislike_count == 0
        assert image.created_at is not None
    
    def test_create_image_with_values(self, db_session):
        """Test creating image with specific values"""
        image = ImageModel(
            picsum_id="237", 
            label="Test Image",
            like_count=10,
            dislike_count=5
        )
        db_session.add(image)
        db_session.commit()
        db_session.refresh(image)
        
        assert image.picsum_id == "237"
        assert image.label == "Test Image"
        assert image.like_count == 10
        assert image.dislike_count == 5
    
    def test_unique_picsum_id_constraint(self, db_session):
        """Test that picsum_id must be unique"""
        image1 = ImageModel(picsum_id="237")
        image2 = ImageModel(picsum_id="237")  # Same picsum_id
        
        db_session.add(image1)
        db_session.commit()
        
        db_session.add(image2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()