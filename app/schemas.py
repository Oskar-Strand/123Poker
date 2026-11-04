from pydantic import BaseModel, Field


class CreateTable(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    max_seats: int = Field(default=8, ge=2, le=8)
    private: bool = False
    password: str | None = Field(default=None, max_length=64)


class JoinTable(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    password: str | None = None
