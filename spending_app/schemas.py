from pydantic import BaseModel, Field


class CheckLimitValueSchema(BaseModel):
    value: int = Field(ge=1, le=9999999)
