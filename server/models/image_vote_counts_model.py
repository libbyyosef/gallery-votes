from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, Boolean
from .base import Base

class ImageVoteCountsModel(Base):
    """
    ORM mapping to the Postgres VIEW public.image_vote_counts.
    Do NOT run Base.metadata.create_all() against this – it already exists.
    """
    __tablename__ = "image_vote_counts"
    __table_args__ = {"extend_existing": True}

    image_id:   Mapped[int]    = mapped_column(Integer, primary_key=True)
    source_url: Mapped[str]    = mapped_column(Text)
    likes:      Mapped[int]    = mapped_column(Integer)
    dislikes:   Mapped[int]    = mapped_column(Integer)
    is_liked:   Mapped[bool]   = mapped_column(Boolean)
    is_disliked:Mapped[bool]   = mapped_column(Boolean)
    net_score:  Mapped[int]    = mapped_column(Integer)
