from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None)

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None)
    is_completed: bool | None = Field(default=None)

class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool
    model_config = {
        "from_attributes": True
    }
