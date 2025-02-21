from logging import Logger
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from configuration.database_config import get_db
from models.db_member import DbMember
from utils.utilities import Singleton


class MemberRepo(metaclass=Singleton):
    """Repository class for handling member-related database operations. Utilizes Singleton pattern to ensure a single instance."""

    def __init__(self):
        """Initializes the MemberRepo with a logger."""
        self.logger = Logger("MemberRepo")

    async def get_member_from_name(self, member_name, member_surname, db: Session):
        """Retrieves a member from the database by name and surname."""
        return db.query(DbMember).filter(DbMember.name.like(member_name), DbMember.surname.like(member_surname)).with_for_update().first()

    async def add_members_bulk(self, members: List[DbMember], db: Session, failure_records: List):
        """Adds multiple members to the database in bulk."""
        try:
            db.bulk_save_objects(members)
            db.commit()
        except Exception as ex:
            db.rollback()
            self.logger.error(f"Failed to Bulk update data due to: {ex}")
            failure_records.append("Failed to bulk upload whole csv. Rollback whole insertion")

    async def add_member_synchronously(self, members: List[DbMember], db: Session, failure_records):
        """Adds members to the database one by one."""
        for mem in members:
            try:
                db.add(mem)
                db.commit()
                db.refresh(mem)
            except Exception as ex:
                db.rollback()
                self.logger.error(f"Failed to insert the row: {mem.__dict__} due to: {ex}")
                failure_records.append(f"Failed to insert the row: {mem.__dict__} due to: {str(ex)[:20]}")

    async def add_member_sync(self, member: DbMember, db: Session):
        """Adds a single member to the database synchronously."""
        db.add(member)
        db.commit()

    async def add_single_member_async(self, member: DbMember, db: AsyncSession):
        """Inserts a single member record asynchronously and returns the result."""
        try:
            db.add(member)
            await db.commit()
            await db.refresh(member)  # Refresh to get the generated ID
            return None
        except Exception as e:
            await db.rollback()
            print(f"Error inserting record: {member.__dict__}, Error: {e}")  # Log error for debugging
            return f"Unable to insert record: {member.__dict__} due to Error: {e}"

    async def get_all_members(self, db: Session):
        return db.query(DbMember).all()