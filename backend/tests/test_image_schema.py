import pytest
from pydantic import ValidationError
from server.schemas.image_schema import ImageSchema

class TestImageSchemaValidation:
    """Test ImageSchema validation"""
    
    def test_image_schema_valid(self):
        """Test ImageSchema with valid data"""
        data = {
            "image_id": 1,
            "source_url": "https://picsum.photos/id/237/600/400.webp",
            "likes": 5,
            "dislikes": 2,
            "is_liked": False,
            "is_disliked": False
        }
        
        schema = ImageSchema(**data)
        
        assert schema.image_id == 1
        assert schema.source_url == data["source_url"]
        assert schema.likes == 5
        assert schema.dislikes == 2
        assert schema.is_liked is False
        assert schema.is_disliked is False
    
    def test_image_schema_defaults(self):
        """Test ImageSchema with default values"""
        data = {
            "image_id": 1,
            "source_url": "https://picsum.photos/id/237/600/400.webp",
            "likes": 5,
            "dislikes": 2
        }
        
        schema = ImageSchema(**data)
        
        assert schema.is_liked is False  # default
        assert schema.is_disliked is False  # default
    
    def test_image_schema_invalid_types(self):
        """Test ImageSchema with invalid data types"""
        with pytest.raises(ValidationError):
            ImageSchema(
                image_id="not_an_int",  # Should be int
                source_url="https://example.com",
                likes=5,
                dislikes=2
            )
        
        with pytest.raises(ValidationError):
            ImageSchema(
                image_id=1,
                source_url=123,  # Should be string
                likes=5,
                dislikes=2
            )
        
        with pytest.raises(ValidationError):
            ImageSchema(
                image_id=1,
                source_url="https://example.com",
                likes="five",  # Should be int
                dislikes=2
            )
    
    def test_image_schema_negative_numbers(self):
        """Test ImageSchema handles negative numbers"""
        # Should allow negative numbers (edge case)
        data = {
            "image_id": 1,
            "source_url": "https://example.com",
            "likes": -1,
            "dislikes": -2
        }
        
        schema = ImageSchema(**data)
        assert schema.likes == -1
        assert schema.dislikes == -2
    
    def test_image_schema_from_model(self, db_session, sample_images):
        """Test ImageSchema.model_validate with ImageModel"""
        image_model = sample_images[0]
        
        schema = ImageSchema.model_validate(image_model, from_attributes=True)
        
        assert schema.image_id == image_model.image_id
        assert schema.source_url == image_model.source_url
        assert schema.likes == image_model.likes
        assert schema.dislikes == image_model.dislikes
        assert schema.is_liked == image_model.is_liked
        assert schema.is_disliked == image_model.is_disliked
    
    def test_image_schema_extra_fields_ignored(self):
        """Test that extra fields are ignored due to extra='ignore'"""
        data = {
            "image_id": 1,
            "source_url": "https://example.com",
            "likes": 5,
            "dislikes": 2,
            "extra_field": "should be ignored"
        }
        
        schema = ImageSchema(**data)
        assert not hasattr(schema, "extra_field")
