
from sqlalchemy import Column, Integer, DateTime, UniqueConstraint, PrimaryKeyConstraint, String
from sqlalchemy.orm import relationship

from configuration.database_config import Base

class DbInventory(Base):
    __tablename__ = "Inventory"
    __table_args__ = ( UniqueConstraint('title', name="uniqueTitle"),)
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String)
    remaining_count = Column(Integer, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    bookings = relationship("DbBooking", back_populates="inventory")

