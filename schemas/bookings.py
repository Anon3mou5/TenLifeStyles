from datetime import datetime

from pydantic import BaseModel


class BookingBase(BaseModel):
        member_id: int
        inventory_id: int
        booked_at: datetime
        booking_reference: str

        class Config():
            from_attributes = True