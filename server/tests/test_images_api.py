# tests/test_images_api.py
from typing import List

def test_get_all_images_empty(client):
    resp = client.get("/images/get_all_images")
    assert resp.status_code == 200
    assert resp.json() == []

def test_get_all_images_with_rows(client, seed_images):
    resp = client.get("/images/get_all_images")
    assert resp.status_code == 200
    data = resp.json()
    # three seeded
    assert len(data) == 3
    # check shape & computed fields
    first = data[0]
    assert {"image_id", "source_url", "likes", "dislikes", "is_liked", "is_disliked"} <= set(first.keys())
    assert first["likes"] == 0 and first["dislikes"] == 0
    # URL should be a Picsum id-based URL with 600/400.webp
    assert "/600/400.webp" in first["source_url"]
    assert "/id/" in first["source_url"]

def test_like_unlike_flow(client, seed_images):
    image_id = seed_images[0]

    # like increments
    r1 = client.post(f"/images/like/{image_id}")
    assert r1.status_code == 200 and r1.json() == {"ok": True}

    # counters endpoint reflects +1 like
    r2 = client.get("/images/counters", params=[("ids", image_id)])
    assert r2.status_code == 200
    arr = r2.json()
    assert isinstance(arr, list) and len(arr) == 1
    assert arr[0]["image_id"] == image_id
    assert arr[0]["likes"] == 1 and arr[0]["dislikes"] == 0

    # unlike decrements (not below 0)
    r3 = client.post(f"/images/unlike/{image_id}")
    assert r3.status_code == 200

    r4 = client.get("/images/counters", params=[("ids", image_id)])
    assert r4.status_code == 200
    assert r4.json()[0]["likes"] == 0 and r4.json()[0]["dislikes"] == 0

    # extra unlike should clamp at 0
    r5 = client.post(f"/images/unlike/{image_id}")
    assert r5.status_code == 200
    r6 = client.get("/images/counters", params=[("ids", image_id)])
    assert r6.json()[0]["likes"] == 0

def test_dislike_undislike_flow(client, seed_images):
    image_id = seed_images[1]

    r1 = client.post(f"/images/dislike/{image_id}")
    assert r1.status_code == 200

    r2 = client.get("/images/counters", params=[("ids", image_id)])
    assert r2.status_code == 200
    assert r2.json()[0]["dislikes"] == 1 and r2.json()[0]["likes"] == 0

    r3 = client.post(f"/images/undislike/{image_id}")
    assert r3.status_code == 200

    r4 = client.get("/images/counters", params=[("ids", image_id)])
    assert r4.json()[0]["dislikes"] == 0 and r4.json()[0]["likes"] == 0

def test_like_404_for_missing_image(client):
    # Choose a large id unlikely to exist (no seed called here)
    r = client.post("/images/like/999999")
    assert r.status_code == 404
    body = r.json()
    assert body.get("detail") == "image_id not found"

def test_counters_multiple_ids(client, seed_images):
    ids: List[int] = seed_images
    # bump some counts
    client.post(f"/images/like/{ids[0]}")
    client.post(f"/images/dislike/{ids[1]}")
    client.post(f"/images/like/{ids[2]}")
    client.post(f"/images/like/{ids[2]}")  # two likes on the third

    # ask for all three
    params = [("ids", i) for i in ids]
    r = client.get("/images/counters", params=params)
    assert r.status_code == 200
    rows = r.json()
    # Should be ordered by image_id (backend does ORDER BY)
    got_ids = [row["image_id"] for row in rows]
    assert got_ids == sorted(ids)

    # quick sanity of counts
    m = {row["image_id"]: row for row in rows}
    assert m[ids[0]]["likes"] == 1 and m[ids[0]]["dislikes"] == 0
    assert m[ids[1]]["likes"] == 0 and m[ids[1]]["dislikes"] == 1
    assert m[ids[2]]["likes"] == 2 and m[ids[2]]["dislikes"] == 0
