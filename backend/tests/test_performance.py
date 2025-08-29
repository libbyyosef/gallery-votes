import pytest
import time
from server.models.image_model import ImageModel

class TestPerformance:
    """Basic performance tests"""
    
    def test_bulk_voting_performance(self, client, sample_images):
        """Test performance with multiple votes"""
        image_id = sample_images[0].image_id
        
        start_time = time.time()
        
        # Perform 50 votes
        for _ in range(50):
            response = client.post(f"/images/like/{image_id}")
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (adjust threshold as needed)
        assert elapsed < 5.0  # 5 seconds for 50 votes
        
        # Verify all votes were recorded
        response = client.get("/images/get_all_images")
        images = response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["likes"] == 55  # 5 original + 50 new
    
    def test_get_all_images_with_many_images(self, db_session):
        """Test get_all_images performance with many images"""
        # Create 100 images
        images = []
        for i in range(100):
            images.append(ImageModel(
                picsum_id=str(i),
                like_count=i % 10,
                dislike_count=i % 5
            ))
        
        db_session.add_all(images)
        db_session.commit()
        
        from server.crud import image_crud
        
        start_time = time.time()
        result = image_crud.get_all_images(db_session)
        elapsed = time.time() - start_time
        
        assert len(result) == 100
        assert elapsed < 1.0  # Should complete within 1 second
    
    def test_csv_export_performance(self, db_session):
        """Test CSV export performance with many images"""
        # Create 50 images
        images = []
        for i in range(50):
            images.append(ImageModel(
                picsum_id=str(i),
                like_count=i * 2,
                dislike_count=i
            ))
        
        db_session.add_all(images)
        db_session.commit()
        
        from server.crud import image_crud
        
        start_time = time.time()
        response = image_crud.export_votes_as_csv(db_session)
        elapsed = time.time() - start_time
        
        assert response.media_type == "text/csv"
        assert elapsed < 2.0  # Should complete within 2 seconds
        
        # Verify CSV content
        content = response.body.decode()
        lines = content.strip().split('\n')
        assert len(lines) == 51  # Header + 50 images