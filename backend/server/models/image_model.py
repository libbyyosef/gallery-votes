# server/models/image_model.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from server.models.base import Base

W, H, FMT = 600, 400, "webp"

class ImageModel(Base):
    __tablename__ = "images"

    image_id       = Column(Integer, primary_key=True, index=True)
    picsum_id      = Column(String, unique=True, nullable=False)
    label          = Column(String, nullable=True)

    like_count     = Column(Integer, nullable=False, default=0)
    dislike_count  = Column(Integer, nullable=False, default=0)

    created_at     = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # ---------- computed attributes used by ImageSchema ----------
    @property
    def source_url(self) -> str:
        return f"https://picsum.photos/id/{self.picsum_id}/{W}/{H}.{FMT}"

    @property
    def likes(self) -> int:
        return int(self.like_count or 0)

    @property
    def dislikes(self) -> int:
        return int(self.dislike_count or 0)

    @property
    def is_liked(self) -> bool:
        # no per-user state; keep false so schema shape is stable
        return False

    @property
    def is_disliked(self) -> bool:
        return False
