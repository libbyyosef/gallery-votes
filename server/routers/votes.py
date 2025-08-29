from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.db.db import get_db
from server.schemas.vote_schema import VoteSchema, VoteUpdateSchema, ActionResultSchema
from server.crud import vote_crud

router = APIRouter(tags=["votes"])


# ----- create -----

@router.post("/votes", response_model=ActionResultSchema, status_code=201)
def create_vote_route(payload: VoteSchema, db: Session = Depends(get_db)):
    return vote_crud.create_vote(db, payload)

# convenience endpoints (no body; action in path)
@router.post("/votes/{image_id}/like", response_model=ActionResultSchema, status_code=201)
def like_image_route(image_id: int, db: Session = Depends(get_db)):
    return vote_crud.create_like(db, image_id)

@router.post("/votes/{image_id}/dislike", response_model=ActionResultSchema, status_code=201)
def dislike_image_route(image_id: int, db: Session = Depends(get_db)):
    return vote_crud.create_dislike(db, image_id)

# ----- update -----

@router.put("/votes/{vote_id}", response_model=ActionResultSchema)
def update_vote_action_route(vote_id: int, payload: VoteUpdateSchema, db: Session = Depends(get_db)):
    return vote_crud.update_vote_action(db, vote_id, payload)

@router.put("/votes/{vote_id}/like", response_model=ActionResultSchema)
def set_vote_like_route(vote_id: int, db: Session = Depends(get_db)):
    return vote_crud.set_vote_like(db, vote_id)

@router.put("/votes/{vote_id}/dislike", response_model=ActionResultSchema)
def set_vote_dislike_route(vote_id: int, db: Session = Depends(get_db)):
    return vote_crud.set_vote_dislike(db, vote_id)

# ----- get -----

@router.get("/export_votes_as_csv")
def export_votes_as_csv(db: Session = Depends(get_db)):
    return vote_crud.export_votes_as_csv(db)  

