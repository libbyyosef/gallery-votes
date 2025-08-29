import pytest
from fastapi.testclient import TestClient

class TestIntegrationWorkflow:
    """Test complete workflows combining multiple operations"""
    
    def test_complete_voting_workflow(self, client, sample_images):
        """Test a complete voting workflow"""
        image_id = sample_images[1].image_id  # starts with 0 likes, 0 dislikes
        
        # 1. Get initial state
        response = client.get("/images/get_all_images")
        images = response.json()
        initial_image = next(img for img in images if img["image_id"] == image_id)
        assert initial_image["likes"] == 0
        assert initial_image["dislikes"] == 0
        
        # 2. Like the image multiple times
        for _ in range(3):
            response = client.post(f"/images/like/{image_id}")
            assert response.status_code == 200
        
        # 3. Dislike the image once
        response = client.post(f"/images/dislike/{image_id}")
        assert response.status_code == 200
        
        # 4. Unlike once
        response = client.post(f"/images/unlike/{image_id}")
        assert response.status_code == 200
        
        # 5. Verify final state
        response = client.get("/images/get_all_images")
        images = response.json()
        final_image = next(img for img in images if img["image_id"] == image_id)
        assert final_image["likes"] == 2  # 3 likes - 1 unlike
        assert final_image["dislikes"] == 1
    
    def test_csv_export_after_voting(self, client, sample_images):
        """Test CSV export reflects voting changes"""
        image_id = sample_images[0].image_id
        
        # Vote on image
        client.post(f"/images/like/{image_id}")
        client.post(f"/images/dislike/{image_id}")
        
        # Export CSV
        response = client.get("/images/export_votes_as_csv")
        assert response.status_code == 200
        
        content = response.text
        lines = content.strip().split('\n')
        
        # Find the row for our image
        image_row = None
        for line in lines[1:]:  # Skip header
            if f"https://picsum.photos/id/237/" in line:
                image_row = line
                break
        
        assert image_row is not None
        assert "6" in image_row  # 5 + 1 likes
        assert "3" in image_row  # 2 + 1 dislikes
    
    def test_counters_endpoint_after_voting(self, client, sample_images):
        """Test counters endpoint reflects voting changes"""
        image_id = sample_images[1].image_id
        
        # Vote on image
        client.post(f"/images/like/{image_id}")
        client.post(f"/images/like/{image_id}")
        
        # Get counters
        response = client.get(f"/images/counters?ids={image_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["image_id"] == image_id
        assert data[0]["likes"] == 2
        assert data[0]["dislikes"] == 0

class TestErrorHandling:
    """Test error handling across the application"""
    
    def test_voting_on_nonexistent_image_consistent(self, client):
        """Test that all vote endpoints handle nonexistent images consistently"""
        nonexistent_id = 999
        
        endpoints = [
            f"/images/like/{nonexistent_id}",
            f"/images/unlike/{nonexistent_id}",
            f"/images/dislike/{nonexistent_id}",
            f"/images/undislike/{nonexistent_id}"
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint)
            assert response.status_code == 404
            data = response.json()
            assert "image_id not found" in data["detail"]
    
    def test_malformed_requests(self, client):
        """Test handling of malformed requests"""
        # Non-numeric image ID
        response = client.post("/images/like/not-a-number")
        assert response.status_code == 422  # Validation error
        
        # Negative image ID
        response = client.post("/images/like/-1")
        assert response.status_code == 404  # Not found (passes validation)
    
    def test_empty_database_operations(self, client):
        """Test operations on empty database"""
        # Get all images
        response = client.get("/images/get_all_images")
        assert response.status_code == 200
        assert response.json() == []
        
        # Export CSV
        response = client.get("/images/export_votes_as_csv")
        assert response.status_code == 200
        content = response.text
        lines = content.strip().split('\n')
        assert len(lines) == 1  # Just header
        
        # Get counters with empty list
        response = client.get("/images/counters")
        assert response.status_code == 422  # Missing required parameter