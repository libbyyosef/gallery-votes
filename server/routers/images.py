from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.db.db import get_db
from server.schemas.image_schema import ImageSchema
from server.crud import image_crud

router = APIRouter(tags=["images"])

@router.get("/get_all_images", response_model=List[ImageSchema])
def get_all_images_route(db: Session = Depends(get_db)):
    return image_crud.get_all_images(db) 
