from pydantic import BaseModel, ConfigDict

class ImageSchema(BaseModel):
    image_id: int
    source_url: str
    likes: int
    dislikes: int
    is_liked: bool = False
    is_disliked: bool = False

    model_config = ConfigDict(from_attributes=True, extra="ignore")
