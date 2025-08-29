from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from server.models import ImageVoteCountsModel
from server.schemas.image_schema import ImageSchema

def get_all_images(db: Session) -> List[ImageSchema]:
    rows = db.execute(
        select(ImageVoteCountsModel).order_by(ImageVoteCountsModel.image_id)
    ).scalars().all()
    return [
        ImageSchema(
            image_id=r.image_id,
            source_url=r.source_url,
            likes=r.likes,
            dislikes=r.dislikes,
            is_liked=r.is_liked,
            is_disliked=r.is_disliked,
            net_score=r.net_score,
        )
        for r in rows
    ]
