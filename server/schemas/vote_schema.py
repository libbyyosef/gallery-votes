from typing import Literal
from pydantic import BaseModel, Field

class VoteSchema(BaseModel):
    image_id: int = Field(ge=1, le=100, description="ID of the image (1..100)")
    action: Literal["like", "dislike"]

class ActionResultSchema(BaseModel):
    ok: bool = True
    message: str | None = None

class VoteUpdateSchema(BaseModel):
    action: Literal["like", "dislike"]