import datetime

from sqlalchemy.orm import Session

from configuration.config import MAX_BOOKINGS
from dto.booking_dto import ItemBookRequestBody, ItemCancelRequest
from models.db_inventory import DbInventory
from models.db_member import DbMember
from repositories.booking_repo import BookingRepo, DbBooking
from repositories.inventory_repo import InventoryRepo
from repositories.member_repo import MemberRepo
from utils.exceptions import MemberNotFoundException, MemberExhaustedLimitException, \
    ItemExpiredException, ItemDepletedException, ItemNotFoundException, BookingNotFoundException
from utils.utilities import Singleton


class BookingService(metaclass=Singleton):
    """
       Service class for handling booking operations.
       Utilizes Singleton pattern to ensure a single instance.
    """
    def __init__(self):
        """
               Initializes the BookingService with repositories for booking, member, and inventory.
        """
        self.booking_repo = BookingRepo()
        self.member_repo = MemberRepo()
        self.inventory_repo = InventoryRepo()

    async def validate_member_and_items(self, request:ItemBookRequestBody,db:Session):
        """
               Validates the member and item for booking.

               Args:
                   request (ItemBookRequestBody): The request body containing member and item details.
                   db (Session): The database session.

               Raises:
                   MemberNotFoundException: If the member is not found in the database.
                   MemberExhaustedLimitException: If the member has reached the maximum booking limit.
                   ItemNotFoundException: If the item is not found in the database.
                   ItemExpiredException: If the item has expired.
                   ItemDepletedException: If the item is depleted.

               Returns:
                   tuple: A tuple containing the validated member and inventory.
        """
        member:DbMember = await self.member_repo.get_member_from_name(request.member_name, request.member_surname,db)
        if not member:
            raise MemberNotFoundException("MemberName provided not present in database")
        if member.booking_count>=int(MAX_BOOKINGS):
            raise MemberExhaustedLimitException("Reached maximum booking limit of " + str(MAX_BOOKINGS))
        inventory:DbInventory = await self.inventory_repo.get_inventory_from_name(request.item_name,db)
        if not inventory:
            raise ItemNotFoundException("ItemName provided not in Database")
        if inventory.expiration_date <= datetime.datetime.utcnow():
            raise ItemExpiredException("item expired")
        if inventory.remaining_count == 0:
            raise ItemDepletedException("item depleted")
        return member,inventory

    async def validate_booking(self,request:ItemCancelRequest,db:Session):
        """
               Validates the booking for cancellation.

               Args:
                   request (ItemCancelRequest): The request body containing booking reference and member details.
                   db (Session): The database session.

               Raises:
                   MemberNotFoundException: If the member is not found in the database.
                   BookingNotFoundException: If the booking is not found in the database.

               Returns:
                   tuple: A tuple containing the validated member, booking order, and inventory.
        """

        member: DbMember = await self.member_repo.get_member_from_name(request.member_name, request.member_surname,db)
        if not member:
            raise MemberNotFoundException("MemberName provided not present in database")

        order: DbBooking = await self.booking_repo.get_booking_from_reference(request.booking_reference,db)
        if not order:
            raise BookingNotFoundException("Booking Id provided not in Database")

        inventory:DbInventory = await self.inventory_repo.get_inventory(order.inventory_id,db)

        return member,order,inventory


    async def book_an_item(self, request:ItemBookRequestBody,db:Session):
        """
                Books an item for a member.

                Args:
                    request (ItemBookRequestBody): The request body containing member and item details.
                    db (Session): The database session.

                Returns:
                    DbBooking: The booking record created.
        """
        member, item = await self.validate_member_and_items(request,db)
        return await self.booking_repo.book_an_item(member,item,db)

    async def cancel_booking(self, request:ItemCancelRequest,db:Session):
        """
                Cancels a booking for a member.

                Args:
                    request (ItemCancelRequest): The request body containing booking reference and member details.
                    db (Session): The database session.

                Returns:
                    DbBooking: The booking record cancelled.
        """
        member, order, inventory = await self.validate_booking(request,db)
        return await self.booking_repo.cancel_an_item(member,order, inventory,db)

    async def view_all_bookings(self, db:Session):
        return await self.booking_repo.get_all_bookings(db)







