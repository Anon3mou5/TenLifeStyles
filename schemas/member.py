from datetime import datetime

from pydantic import BaseModel


class MemberBase(BaseModel):
        id: int
        name: str
        surname: str
        booking_count: int
        date_joined: datetime

        class Config():
            from_attributes = True
