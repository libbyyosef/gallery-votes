# server/scripts/seed_images.py
import requests
from sqlalchemy.dialects.postgresql import insert
from server.db.db import engine
from server.models.image_model import ImageModel

PICSUM_LIST_URL = "https://picsum.photos/v2/list?page=1&limit=100"

def main() -> None:
    # 1) Fetch 100 Picsum IDs
    resp = requests.get(PICSUM_LIST_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    ids = [str(item["id"]) for item in data]

    # 2) Bulk upsert via Core using the model's table (fast & idempotent)
    rows = [{"picsum_id": pid} for pid in ids]
    stmt = (
        insert(ImageModel.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["picsum_id"])
    )

    with engine.begin() as conn:
        result = conn.execute(stmt)

    inserted = getattr(result, "rowcount", None)  # may be -1 on some drivers
    print(f"✅ Seeded {len(ids)} ids (inserted {inserted if inserted is not None else 'some'} new).")

if __name__ == "__main__":
    main()
