from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Query

from server.db.db import get_db
from server.schemas.image_schema import ImageSchema
from server.crud import image_crud

router = APIRouter(prefix="/images", tags=["images"])

# ----- reads -----
@router.get("/get_all_images", response_model=List[ImageSchema])
def get_all_images_route(db: Session = Depends(get_db)):
    return image_crud.get_all_images(db)

# ----- counters-only writes (used by frontend) -----
@router.post("/like/{image_id}")
def like_image_route(image_id: int, db: Session = Depends(get_db)):
    image_crud.like_image(db, image_id)
    return {"ok": True}

@router.post("/unlike/{image_id}")
def unlike_image_route(image_id: int, db: Session = Depends(get_db)):
    image_crud.unlike_image(db, image_id)
    return {"ok": True}

@router.post("/dislike/{image_id}")
def dislike_image_route(image_id: int, db: Session = Depends(get_db)):
    image_crud.dislike_image(db, image_id)
    return {"ok": True}

@router.post("/undislike/{image_id}")
def undislike_image_route(image_id: int, db: Session = Depends(get_db)):
    image_crud.undislike_image(db, image_id)
    return {"ok": True}

@router.get("/counters")
def get_counters_route(
    ids: list[int] = Query(..., description="Repeat ids param: ?ids=1&ids=2"),
    db: Session = Depends(get_db),
):
    return image_crud.get_counters(db, ids)
# ----- CSV export -----
@router.get("/export_votes_as_csv")
def export_votes_as_csv_route(db: Session = Depends(get_db)):
    return image_crud.export_votes_as_csv(db)
