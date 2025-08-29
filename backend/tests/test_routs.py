# # backend/tests/test_routes.py
# def test_get_all_images(client, db_session):
#     # Setup: Add test images
#     images = [
#         ImageModel(image_id=1, picsum_seed="seed1"),
#         ImageModel(image_id=2, picsum_seed="seed2"),
#     ]
#     db_session.add_all(images)
#     db_session.commit()
    
#     # Test API endpoint
#     response = client.get("/images/get_all_images")
    
#     # Assert
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]["image_id"] == 1
#     assert "source_url" in data[0]

# def test_like_image_endpoint(client, db_session):
#     # Setup
#     image = ImageModel(image_id=1, picsum_seed="test")
#     db_session.add(image)
#     db_session.commit()
    
#     # Test like endpoint
#     response = client.post("/votes/like/1")
    
#     # Assert
#     assert response.status_code == 201
#     data = response.json()
#     assert data["ok"] == True

# def test_export_csv(client, db_session):
#     # Setup: Add image and votes
#     image = ImageModel(image_id=1, picsum_seed="test")
#     db_session.add(image)
#     db_session.commit()
    
#     # Add some votes
#     client.post("/votes/like/1")
#     client.post("/votes/dislike/1")
    
#     # Test CSV export
#     response = client.get("/votes/export_votes_as_csv")
    
#     assert response.status_code == 200
#     assert response.headers["content-type"] == "text/csv; charset=utf-8"
#     assert "image_id,source_url,likes,dislikes" in response.text