from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text
from .base import Base

class ImageModel(Base):
    __tablename__ = "images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    label: Mapped[str | None] = mapped_column(Text, nullable=True)
