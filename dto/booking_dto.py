from typing import Optional

from pydantic import BaseModel, validator


class ItemBookRequestBody(BaseModel):
    member_name: str
    member_surname: str
    item_name: str

    @validator('member_name', 'member_surname', 'item_name')
    def must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Field must not be empty')
        return v

class ItemCancelRequest(BaseModel):
    member_name: str
    member_surname: str
    booking_reference: str

    @validator('member_name', 'member_surname', 'booking_reference')
    def must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Field must not be empty')
        return v
