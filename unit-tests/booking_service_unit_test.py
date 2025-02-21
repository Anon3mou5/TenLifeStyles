import unittest, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from dto.booking_dto import ItemBookRequestBody, ItemCancelRequest
from services.booking_service import BookingService
from utils.exceptions import MemberNotFoundException, MemberExhaustedLimitException, ItemExpiredException, \
    ItemDepletedException, ItemNotFoundException, BookingNotFoundException


class TestBookingService(unittest.TestCase):

    def setUp(self):
        self.booking_service = BookingService()
        self.db = MagicMock(spec=Session)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    @patch('repositories.inventory_repo.InventoryRepo.get_inventory_from_name', new_callable=AsyncMock)
    async def test_validate_member_and_items_success(self, mock_get_inventory, mock_get_member):
        mock_get_member.return_value = MagicMock(booking_count=0)
        mock_get_inventory.return_value = MagicMock(
            expiration_date=datetime.datetime.utcnow() + datetime.timedelta(days=1), remaining_count=1)

        request = ItemBookRequestBody(member_name="John", member_surname="Doe", item_name="Book")
        member, inventory = await self.booking_service.validate_member_and_items(request, self.db)

        self.assertIsNotNone(member)
        self.assertIsNotNone(inventory)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    async def test_validate_member_and_items_member_not_found(self, mock_get_member):
        mock_get_member.return_value = None

        request = ItemBookRequestBody(member_name="John", member_surname="Doe", item_name="Book")
        with self.assertRaises(MemberNotFoundException):
            await self.booking_service.validate_member_and_items(request, self.db)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    async def test_validate_member_and_items_member_exhausted_limit(self, mock_get_member):
        mock_get_member.return_value = MagicMock(booking_count=10)

        request = ItemBookRequestBody(member_name="John", member_surname="Doe", item_name="Book")
        with self.assertRaises(MemberExhaustedLimitException):
            await self.booking_service.validate_member_and_items(request, self.db)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    @patch('repositories.inventory_repo.InventoryRepo.get_inventory_from_name', new_callable=AsyncMock)
    async def test_validate_member_and_items_item_not_found(self, mock_get_inventory, mock_get_member):
        mock_get_member.return_value = MagicMock(booking_count=0)
        mock_get_inventory.return_value = None

        request = ItemBookRequestBody(member_name="John", member_surname="Doe", item_name="Book")
        with self.assertRaises(ItemNotFoundException):
            await self.booking_service.validate_member_and_items(request, self.db)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    @patch('repositories.inventory_repo.InventoryRepo.get_inventory_from_name', new_callable=AsyncMock)
    async def test_validate_member_and_items_item_expired(self, mock_get_inventory, mock_get_member):
        mock_get_member.return_value = MagicMock(booking_count=0)
        mock_get_inventory.return_value = MagicMock(
            expiration_date=datetime.datetime.utcnow() - datetime.timedelta(days=1))

        request = ItemBookRequestBody(member_name="John", member_surname="Doe", item_name="Book")
        with self.assertRaises(ItemExpiredException):
            await self.booking_service.validate_member_and_items(request, self.db)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    @patch('repositories.inventory_repo.InventoryRepo.get_inventory_from_name', new_callable=AsyncMock)
    async def test_validate_member_and_items_item_depleted(self, mock_get_inventory, mock_get_member):
        mock_get_member.return_value = MagicMock(booking_count=0)
        mock_get_inventory.return_value = MagicMock(
            expiration_date=datetime.datetime.utcnow() + datetime.timedelta(days=1), remaining_count=0)

        request = ItemBookRequestBody(member_name="John", member_surname="Doe", item_name="Book")
        with self.assertRaises(ItemDepletedException):
            await self.booking_service.validate_member_and_items(request, self.db)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    @patch('repositories.booking_repo.BookingRepo.get_booking_from_reference', new_callable=AsyncMock)
    @patch('repositories.inventory_repo.InventoryRepo.get_inventory', new_callable=AsyncMock)
    async def test_validate_booking_success(self, mock_get_inventory, mock_get_booking, mock_get_member):
        mock_get_member.return_value = MagicMock()
        mock_get_booking.return_value = MagicMock()
        mock_get_inventory.return_value = MagicMock()

        request = ItemCancelRequest(member_name="John", member_surname="Doe", booking_reference="12345")
        member, order, inventory = await self.booking_service.validate_booking(request, self.db)

        self.assertIsNotNone(member)
        self.assertIsNotNone(order)
        self.assertIsNotNone(inventory)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    async def test_validate_booking_member_not_found(self, mock_get_member):
        mock_get_member.return_value = None

        request = ItemCancelRequest(member_name="John", member_surname="Doe", booking_reference="12345")
        with self.assertRaises(MemberNotFoundException):
            await self.booking_service.validate_booking(request, self.db)

    @patch('repositories.member_repo.MemberRepo.get_member_from_name', new_callable=AsyncMock)
    @patch('repositories.booking_repo.BookingRepo.get_booking_from_reference', new_callable=AsyncMock)
    async def test_validate_booking_booking_not_found(self, mock_get_booking, mock_get_member):
        mock_get_member.return_value = MagicMock()
        mock_get_booking.return_value = None

        request = ItemCancelRequest(member_name="John", member_surname="Doe", booking_reference="12345")
        with self.assertRaises(BookingNotFoundException):
            await self.booking_service.validate_booking(request, self.db)


if __name__ == '__main__':
    unittest.main()