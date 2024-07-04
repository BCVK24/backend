from pydantic import BaseModel


class UserBase(BaseModel):
    pass


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    pass
