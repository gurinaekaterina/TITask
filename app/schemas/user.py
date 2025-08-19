from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
