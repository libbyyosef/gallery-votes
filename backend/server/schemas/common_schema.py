from pydantic import BaseModel, ConfigDict

class ActionResultSchema(BaseModel):
    ok: bool

    # pydantic v2: allow from ORM if ever used
    model_config = ConfigDict(from_attributes=True, extra="ignore")
