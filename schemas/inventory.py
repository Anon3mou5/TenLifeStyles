from datetime import datetime

from pydantic import BaseModel


class InventoryBase(BaseModel):
    title: str
    description: str
    remaining_count: int
    expiration_date: datetime
    class Config():
        from_attributes = True
