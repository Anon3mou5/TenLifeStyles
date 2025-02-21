from logging import Logger
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from configuration.database_config import get_db
from models.db_inventory import DbInventory
from utils.utilities import Singleton


class InventoryRepo(metaclass=Singleton):
    """Repository class for handling inventory-related database operations."""

    def __init__(self):
        """Initializes the InventoryRepo with a logger."""
        self.logger = Logger("InventoryRepo")

    async def get_inventory_from_name(self, item_name, db: Session):
        """Retrieves inventory by item name."""
        return db.query(DbInventory).filter(DbInventory.title.like(item_name)).with_for_update().first()

    async def get_inventory(self, id, db: Session):
        """Retrieves inventory by ID."""
        return db.query(DbInventory).filter(DbInventory.id == id).with_for_update().first()

    async def add_inventory_bulk(self, inventory: List[DbInventory], db: Session, failure_records: List):
        """Adds multiple inventory items to the database in bulk."""
        try:
            db.bulk_save_objects(inventory)
            db.commit()
        except Exception as ex:
            db.rollback()
            self.logger.error("Failed to Bulk update data due to: " + str(ex))
            failure_records.append("Failed to insert whole document. Rollback whole insertion")

    async def add_inventory_synchronously(self, inventories: List[DbInventory], db: Session, failure_records):
        """Adds inventory items to the database one by one."""
        for inv in inventories:
            try:
                db.add(inv)
                db.commit()
            except Exception as ex:
                db.rollback()
                self.logger.error("Failed to insert the row: " + str(inv.__dict__) + " due to: " + str(ex))
                failure_records.append("Failed to insert the row: " + str(inv.__dict__) + " due to: " + str(ex)[:20])

    async def add_item_sync(self, inventory: DbInventory, db: Session):
        """Adds a single inventory item to the database synchronously."""
        db.add(inventory)
        db.commit()

    async def add_single_item_asynch(self, item: DbInventory, db: AsyncSession):
        """Inserts a record and returns the data on success, None on failure."""
        try:
            db.add(item)
            await db.commit()
            await db.refresh(item)  # Refresh to get the generated ID
            return None
        except Exception as e:
            await db.rollback()
            print(f"Error inserting record: {item.__dict__}, Error: {e}")  # Log error for debugging
            return f"Unable to insert record: {item.__dict__} due to Error: {e}"


    async def get_all_inventories(self, db: Session):
        return db.query(DbInventory).all()