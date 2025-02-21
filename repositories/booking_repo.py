import uuid
import logging
from typing import List, Type

from sqlalchemy.orm import Session

from configuration.database_config import get_db
from models.db_bookings import DbBooking
from models.db_inventory import DbInventory
from models.db_member import DbMember
from utils.utilities import Singleton


class BookingRepo(metaclass=Singleton):
    """
       Repository for handling booking operations.
    """

    async def get_booking_from_reference(self, reference:str,db:Session):
        """
                Retrieve a booking by its reference.

                :param reference: The booking reference string.
                :param db: The database session.
                :return: The booking object if found, else None.
        """

        return db.query(DbBooking).filter(DbBooking.booking_reference.like(reference)).first()

    async def book_an_item(self, member:DbMember, item:DbInventory,db:Session):
        """
                Book an item for a member.

                :param member: The member object.
                :param item: The inventory item object.
                :param db: The database session.
                :return: The created booking object.

                :raises Exception: If an error occurs during the transaction.
        """
        logging.info(f"Booking item {item.id} for member {member.id}")

        # Proceed with booking
        try:
            booking = DbBooking(member_id=member.id, inventory_id=item.id, booking_reference=uuid.uuid4())
            db.add(booking)

            # Update counts
            member.booking_count += 1
            item.remaining_count -= 1

            # Commit the transaction
            db.commit()
            logging.info(f"Booking successful: {booking.booking_reference}")
        except Exception as ex:
            db.rollback()
            logging.error(f"Booking failed: {ex}")
            raise Exception(ex)
        return booking

    async def cancel_an_item(self, member:DbMember, booking:DbBooking, item:DbInventory,db:Session):
        """
                Cancel a booking for an item.

                :param member: The member object.
                :param booking: The booking object.
                :param item: The inventory item object.
                :param db: The database session.

                :raises Exception: If an error occurs during the transaction.
        """
        logging.info(f"Cancelling booking {booking.booking_reference} for member {member.id}")

        try:
            # Update counts
            member.booking_count -= 1
            item.remaining_count += 1
            db.delete(booking)

            # Commit the transaction
            db.commit()
            logging.info(f"Cancellation successful: {booking.booking_reference}")
        except Exception as ex:
            db.rollback()
            logging.error(f"Cancellation failed: {ex}")
            raise Exception(ex)

    async def get_all_bookings(self,db:Session)-> list[Type[DbBooking]]:
        """
                Retrieve a booking by its reference.

                :param reference: The booking reference string.
                :param db: The database session.
                :return: The booking object if found, else None.
        """

        return db.query(DbBooking).all()


