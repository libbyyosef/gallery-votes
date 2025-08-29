import pytest
from fastapi import HTTPException
from server.crud import image_crud
from server.models.image_model import ImageModel
from server.schemas.image_schema import ImageSchema

class TestImageCrudReads:
    """Test image_crud read operations"""
    
    def test_ensure_image_exists(self, db_session, sample_images):
        """Test _ensure_image with existing image"""
        # Should not raise exception
        image_crud._ensure_image(db_session, sample_images[0].image_id)
    
    def test_ensure_image_not_exists(self, db_session):
        """Test _ensure_image with non-existent image"""
        with pytest.raises(HTTPException) as exc_info:
            image_crud._ensure_image(db_session, 999)
        
        assert exc_info.value.status_code == 404
        assert "image_id not found" in str(exc_info.value.detail)
    
    def test_get_all_images_empty(self, db_session):
        """Test get_all_images with empty database"""
        result = image_crud.get_all_images(db_session)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_get_all_images_with_data(self, db_session, sample_images):
        """Test get_all_images with sample data"""
        result = image_crud.get_all_images(db_session)
        
        assert len(result) == 3
        assert all(isinstance(img, ImageSchema) for img in result)
        
        # Check first image
        first_img = result[0]
        assert first_img.image_id == sample_images[0].image_id
        assert first_img.source_url.startswith("https://picsum.photos/id/237/")
        assert first_img.likes == 5
        assert first_img.dislikes == 2
        assert first_img.is_liked is False
        assert first_img.is_disliked is False
    
    def test_get_counters_empty_list(self, db_session):
        """Test get_counters with empty ID list"""
        result = image_crud.get_counters(db_session, [])
        
        assert result == []
    
    def test_get_counters_with_valid_ids(self, db_session, sample_images):
        """Test get_counters with valid image IDs"""
        ids = [sample_images[0].image_id, sample_images[2].image_id]
        result = image_crud.get_counters(db_session, ids)
        
        assert len(result) == 2
        assert result[0]["image_id"] == sample_images[0].image_id
        assert result[0]["likes"] == 5
        assert result[0]["dislikes"] == 2
        
        assert result[1]["image_id"] == sample_images[2].image_id
        assert result[1]["likes"] == 10
        assert result[1]["dislikes"] == 1
    
    def test_get_counters_with_invalid_ids(self, db_session, sample_images):
        """Test get_counters with non-existent IDs"""
        result = image_crud.get_counters(db_session, [999, 1000])
        
        assert result == []

class TestImageCrudLikes:
    """Test image_crud like operations"""
    
    def test_like_image_success(self, db_session, sample_images):
        """Test like_image increments counter"""
        image_id = sample_images[1].image_id  # starts with 0 likes
        
        result = image_crud.like_image(db_session, image_id)
        
        assert result.ok is True
        
        # Check database was updated
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.like_count == 1
        assert updated_image.dislike_count == 0  # unchanged
    
    def test_like_image_multiple_times(self, db_session, sample_images):
        """Test like_image can be called multiple times"""
        image_id = sample_images[0].image_id  # starts with 5 likes
        
        # Like twice
        image_crud.like_image(db_session, image_id)
        image_crud.like_image(db_session, image_id)
        
        # Check database
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.like_count == 7  # 5 + 2
    
    def test_like_image_invalid_id(self, db_session):
        """Test like_image with non-existent image"""
        with pytest.raises(HTTPException) as exc_info:
            image_crud.like_image(db_session, 999)
        
        assert exc_info.value.status_code == 404
    
    def test_unlike_image_success(self, db_session, sample_images):
        """Test unlike_image decrements counter"""
        image_id = sample_images[0].image_id  # starts with 5 likes
        
        result = image_crud.unlike_image(db_session, image_id)
        
        assert result.ok is True
        
        # Check database
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.like_count == 4  # 5 - 1
    
    def test_unlike_image_at_zero(self, db_session, sample_images):
        """Test unlike_image doesn't go below zero"""
        image_id = sample_images[1].image_id  # starts with 0 likes
        
        result = image_crud.unlike_image(db_session, image_id)
        
        assert result.ok is True
        
        # Check it stays at 0
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.like_count == 0
    
    def test_unlike_image_invalid_id(self, db_session):
        """Test unlike_image with non-existent image"""
        with pytest.raises(HTTPException) as exc_info:
            image_crud.unlike_image(db_session, 999)
        
        assert exc_info.value.status_code == 404

class TestImageCrudDislikes:
    """Test image_crud dislike operations"""
    
    def test_dislike_image_success(self, db_session, sample_images):
        """Test dislike_image increments counter"""
        image_id = sample_images[1].image_id  # starts with 0 dislikes
        
        result = image_crud.dislike_image(db_session, image_id)
        
        assert result.ok is True
        
        # Check database
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.dislike_count == 1
        assert updated_image.like_count == 0  # unchanged
    
    def test_dislike_image_invalid_id(self, db_session):
        """Test dislike_image with non-existent image"""
        with pytest.raises(HTTPException) as exc_info:
            image_crud.dislike_image(db_session, 999)
        
        assert exc_info.value.status_code == 404
    
    def test_undislike_image_success(self, db_session, sample_images):
        """Test undislike_image decrements counter"""
        image_id = sample_images[0].image_id  # starts with 2 dislikes
        
        result = image_crud.undislike_image(db_session, image_id)
        
        assert result.ok is True
        
        # Check database
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.dislike_count == 1  # 2 - 1
    
    def test_undislike_image_at_zero(self, db_session, sample_images):
        """Test undislike_image doesn't go below zero"""
        image_id = sample_images[1].image_id  # starts with 0 dislikes
        
        result = image_crud.undislike_image(db_session, image_id)
        
        assert result.ok is True
        
        # Check it stays at 0
        updated_image = db_session.get(ImageModel, image_id)
        assert updated_image.dislike_count == 0
    
    def test_undislike_image_invalid_id(self, db_session):
        """Test undislike_image with non-existent image"""
        with pytest.raises(HTTPException) as exc_info:
            image_crud.undislike_image(db_session, 999)
        
        assert exc_info.value.status_code == 404


    
    