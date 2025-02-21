from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from configuration.database_config import Base

class DbBooking(Base):
    __tablename__ = 'Bookings'

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey('Members.id'))
    inventory_id = Column(Integer, ForeignKey('Inventory.id'))
    booked_at = Column(DateTime, default=datetime.utcnow)
    booking_reference = Column(String, nullable=False, unique=True, index=True)
    member = relationship("DbMember", back_populates="bookings")
    inventory = relationship("DbInventory", back_populates="bookings")
