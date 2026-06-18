from pydantic import BaseModel, ConfigDict


class TokenPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
