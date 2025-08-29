# server/crud/image_crud.py
from typing import List, Dict
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from server.models.image_model import ImageModel
from server.schemas.image_schema import ImageSchema
from server.schemas.common_schema import ActionResultSchema

def _ensure_image(db: Session, image_id: int) -> None:
    row = db.execute(text("SELECT 1 FROM public.images WHERE image_id = :iid"), {"iid": image_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="image_id not found")

# ----- reads -----

def get_all_images(db: Session) -> List[ImageSchema]:
    items = db.execute(
        select(ImageModel).order_by(ImageModel.image_id)
    ).scalars().all()

    # thanks to the computed properties on ImageModel and pydantic v2 from_attributes=True
    return [ImageSchema.model_validate(obj, from_attributes=True) for obj in items]

def get_counters(db: Session, ids: list[int]) -> list[dict]:
    if not ids:
        return []
    rows = db.execute(
        select(
            ImageModel.image_id,
            ImageModel.like_count,
            ImageModel.dislike_count,
        )
        .where(ImageModel.image_id.in_(ids))
        .order_by(ImageModel.image_id)
    ).all()
    return [{"image_id": r[0], "likes": r[1], "dislikes": r[2]} for r in rows]

# ----- counters-only writes -----

def like_image(db: Session, image_id: int) -> ActionResultSchema:
    _ensure_image(db, image_id)
    db.execute(text("UPDATE public.images SET like_count = like_count + 1 WHERE image_id = :iid"), {"iid": image_id})
    db.commit()
    return ActionResultSchema(ok=True)

def dislike_image(db: Session, image_id: int) -> ActionResultSchema:
    _ensure_image(db, image_id)
    db.execute(text("UPDATE public.images SET dislike_count = dislike_count + 1 WHERE image_id = :iid"), {"iid": image_id})
    db.commit()
    return ActionResultSchema(ok=True)

def unlike_image(db: Session, image_id: int) -> ActionResultSchema:
    _ensure_image(db, image_id)
    db.execute(text("UPDATE public.images SET like_count = GREATEST(like_count - 1, 0) WHERE image_id = :iid"), {"iid": image_id})
    db.commit()
    return ActionResultSchema(ok=True)

def undislike_image(db: Session, image_id: int) -> ActionResultSchema:
    _ensure_image(db, image_id)
    db.execute(text("UPDATE public.images SET dislike_count = GREATEST(dislike_count - 1, 0) WHERE image_id = :iid"), {"iid": image_id})
    db.commit()
    return ActionResultSchema(ok=True)

# ----- CSV export -----

def export_votes_as_csv(db: Session) -> Response:
    items = get_all_images(db)  # list[ImageSchema]

    import csv
    from io import StringIO
    buf = StringIO()

    fieldnames = [
        "Image URL",
        "Likes",
        "Dislikes",
        "Is Current User Liked",
        "Is Current User Dislike",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()

    for item in items:
        writer.writerow({
            "Image URL": item.source_url,
            "Likes": item.likes,
            "Dislikes": item.dislikes,
            "Is Current User Liked": item.is_liked,
            "Is Current User Dislike": item.is_disliked,
        })

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=votes.csv"},
    )
