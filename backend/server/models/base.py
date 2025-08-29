from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import ENUM

class Base(DeclarativeBase):
    pass

# Map to the existing DB enum created by schema.sql
vote_action_enum = ENUM('like', 'dislike', name='vote_action', create_type=False)
