

from sqlalchemy import Column, Integer, DateTime, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import relationship

from configuration.database_config import Base


class DbMember(Base):
    __tablename__ = "Members"
    __table_args__ = ( UniqueConstraint("name", "surname"),)
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, index=True)
    surname = Column(String, nullable=False, index=True)
    booking_count = Column(Integer, nullable=False)
    date_joined = Column(DateTime,nullable=False)
    bookings = relationship("DbBooking", back_populates="member")