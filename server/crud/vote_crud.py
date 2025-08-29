import csv
from io import StringIO
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, Response

from server.models.image_model import ImageModel
from server.models.vote_model import VoteModel
from server.schemas.vote_schema import VoteSchema, VoteUpdateSchema,ActionResultSchema
from server.models.image_vote_counts_model import ImageVoteCountsModel
from server.schemas.image_schema import ImageSchema

# ---------- CREATE ----------

def create_vote(db: Session, payload: VoteSchema) -> ActionResultSchema:
    # ensure image exists
    exists = db.execute(
        select(ImageModel.image_id).where(ImageModel.image_id == payload.image_id)
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="image_id not found")

    db.add(VoteModel(image_id=payload.image_id, action=payload.action))
    db.commit()
    return ActionResultSchema(ok=True)

# convenience helpers for one-liner endpoints
def create_like(db: Session, image_id: int) -> ActionResultSchema:
    return create_vote(db, VoteSchema(image_id=image_id, action="like"))

def create_dislike(db: Session, image_id: int) -> ActionResultSchema:
    return create_vote(db, VoteSchema(image_id=image_id, action="dislike"))

# ---------- UPDATE ----------

def update_vote_action(db: Session, vote_id: int, payload: VoteUpdateSchema) -> ActionResultSchema:
    vote = db.get(VoteModel, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="vote_id not found")

    vote.action = payload.action
    db.commit()
    return ActionResultSchema(ok=True)

# convenience helpers
def set_vote_like(db: Session, vote_id: int) -> ActionResultSchema:
    return update_vote_action(db, vote_id, VoteUpdateSchema(action="like"))

def set_vote_dislike(db: Session, vote_id: int) -> ActionResultSchema:
    return update_vote_action(db, vote_id, VoteUpdateSchema(action="dislike"))


def export_votes_as_csv(db: Session) -> Response:
    rows = db.execute(
        select(ImageVoteCountsModel).order_by(ImageVoteCountsModel.image_id)
    ).scalars().all()     # ORM objects from the view

    buf = StringIO()
    # Pydantic v2: schema fields in defined order
    fieldnames = list(ImageSchema.model_fields.keys())
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()

    for obj in rows:
        item = ImageSchema.model_validate(obj, from_attributes=True)
        writer.writerow(item.model_dump())

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=votes.csv"},
    )