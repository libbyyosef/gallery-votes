from pydantic import BaseModel

class ImageSchema(BaseModel):
    image_id: int
    source_url: str
    likes: int
    dislikes: int
    is_liked: bool
    is_disliked: bool
    net_score: int
