from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, ForeignKey
from .base import Base, vote_action_enum

class VoteModel(Base):
    __tablename__ = "votes"

    vote_id: Mapped[int]  = mapped_column(BigInteger, primary_key=True)
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.image_id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str]   = mapped_column(vote_action_enum, nullable=False)  # 'like' | 'dislike'
