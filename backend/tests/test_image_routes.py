import pytest
from fastapi.testclient import TestClient

class TestImageRoutesGet:
    """Test image API GET routes"""
    
    def test_get_all_images_empty(self, client):
        """Test GET /images/get_all_images with empty database"""
        response = client.get("/images/get_all_images")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_images_with_data(self, client, sample_images):
        """Test GET /images/get_all_images with sample data"""
        response = client.get("/images/get_all_images")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Check first image structure
        first_img = data[0]
        required_fields = ["image_id", "source_url", "likes", "dislikes", "is_liked", "is_disliked"]
        for field in required_fields:
            assert field in first_img
        
        assert first_img["likes"] == 5
        assert first_img["dislikes"] == 2
        assert first_img["is_liked"] is False
    
    def test_get_counters_success(self, client, sample_images):
        """Test GET /images/counters"""
        ids = [sample_images[0].image_id, sample_images[2].image_id]
        
        response = client.get(f"/images/counters?ids={ids[0]}&ids={ids[1]}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        assert data[0]["image_id"] == sample_images[0].image_id
        assert data[0]["likes"] == 5
        assert data[0]["dislikes"] == 2
    
    def test_get_counters_empty_list(self, client):
        """Test GET /images/counters with no IDs"""
        response = client.get("/images/counters")
        
        # Should return 422 because ids parameter is required
        assert response.status_code == 422
    
    def test_export_csv_endpoint(self, client, sample_images):
        """Test GET /images/export_votes_as_csv"""
        response = client.get("/images/export_votes_as_csv")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment; filename=votes.csv" in response.headers["content-disposition"]
        
        content = response.text
        lines = content.strip().split('\n')
        assert len(lines) == 4  # Header + 3 images
        
        # Check header exists
        assert "Image URL" in lines[0]
        assert "Likes" in lines[0]
        assert "Dislikes" in lines[0]

class TestImageRoutesLike:
    """Test image API like/unlike routes"""
    
    def test_like_image_success(self, client, sample_images):
        """Test POST /images/like/{image_id}"""
        image_id = sample_images[1].image_id
        
        response = client.post(f"/images/like/{image_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify the like was recorded
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["likes"] == 1  # was 0, now 1
    
    def test_like_image_multiple_times(self, client, sample_images):
        """Test POST /images/like/{image_id} multiple times"""
        image_id = sample_images[1].image_id
        
        # Like three times
        for _ in range(3):
            response = client.post(f"/images/like/{image_id}")
            assert response.status_code == 200
        
        # Verify all likes were recorded
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["likes"] == 3
    
    def test_like_image_invalid_id(self, client):
        """Test POST /images/like/{image_id} with invalid ID"""
        response = client.post("/images/like/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "image_id not found" in data["detail"]
    
    def test_unlike_image_success(self, client, sample_images):
        """Test POST /images/unlike/{image_id}"""
        image_id = sample_images[0].image_id  # has 5 likes
        
        response = client.post(f"/images/unlike/{image_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify the unlike was recorded
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["likes"] == 4  # was 5, now 4
    
    def test_unlike_image_at_zero(self, client, sample_images):
        """Test POST /images/unlike/{image_id} when already at zero"""
        image_id = sample_images[1].image_id  # has 0 likes
        
        response = client.post(f"/images/unlike/{image_id}")
        
        assert response.status_code == 200
        
        # Verify it stayed at zero
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["likes"] == 0
    
    def test_unlike_image_invalid_id(self, client):
        """Test POST /images/unlike/{image_id} with invalid ID"""
        response = client.post("/images/unlike/999")
        
        assert response.status_code == 404

class TestImageRoutesDislike:
    """Test image API dislike/undislike routes"""
    
    def test_dislike_image_success(self, client, sample_images):
        """Test POST /images/dislike/{image_id}"""
        image_id = sample_images[1].image_id
        
        response = client.post(f"/images/dislike/{image_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify the dislike was recorded
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["dislikes"] == 1  # was 0, now 1
    
    def test_dislike_image_invalid_id(self, client):
        """Test POST /images/dislike/{image_id} with invalid ID"""
        response = client.post("/images/dislike/999")
        
        assert response.status_code == 404
    
    def test_undislike_image_success(self, client, sample_images):
        """Test POST /images/undislike/{image_id}"""
        image_id = sample_images[0].image_id  # has 2 dislikes
        
        response = client.post(f"/images/undislike/{image_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify the undislike was recorded
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["dislikes"] == 1  # was 2, now 1
    
    def test_undislike_image_at_zero(self, client, sample_images):
        """Test POST /images/undislike/{image_id} when already at zero"""
        image_id = sample_images[1].image_id  # has 0 dislikes
        
        response = client.post(f"/images/undislike/{image_id}")
        
        assert response.status_code == 200
        
        # Verify it stayed at zero
        images_response = client.get("/images/get_all_images")
        images = images_response.json()
        updated_image = next(img for img in images if img["image_id"] == image_id)
        assert updated_image["dislikes"] == 0
    
    def test_undislike_image_invalid_id(self, client):
        """Test POST /images/undislike/{image_id} with invalid ID"""
        response = client.post("/images/undislike/999")
        
        assert response.status_code == 404