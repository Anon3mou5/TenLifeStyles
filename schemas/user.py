from pydantic import BaseModel


class UserBase(BaseModel):
        id: int
        username: str
        fullname: str
        email: str
        password: str

        class Config():
            from_attributes = True