from pydantic import BaseModel, ConfigDict

class ActionResultSchema(BaseModel):
    ok: bool

    model_config = ConfigDict(from_attributes=True, extra="ignore")
