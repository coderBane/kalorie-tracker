from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    name: str = Field(max_length=256, min_length=4)
    description: str | None = None


class RoleUpdate(BaseModel):
    description: str | None = None
    