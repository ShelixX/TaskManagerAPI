from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=8, max_length=30)

class UserUpdate(BaseModel):
    username: str | None = Field(min_length=5, max_length=20)
    password: str | None = Field(min_length=8, max_length=30)
    is_active: bool | None = Field(default=None)

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    model_config = {
        "from_attributes": True
    }

class CurrentUserResponse(BaseModel):
    message: str | None = None
    user_data: UserRead