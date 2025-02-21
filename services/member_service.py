import asyncio
from datetime import datetime
from logging import Logger
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models.db_member import DbMember
from repositories.member_repo import MemberRepo
from utils.utilities import Singleton, validate_csv_return_dataframe


class MemberService(metaclass=Singleton):
    """
       Service class for handling member operations.
       Utilizes Singleton pattern to ensure a single instance.
    """
    def __init__(self):
        """
               Initializes the MemberService with a member repository and a logger.
        """
        self.member_repo = MemberRepo()
        self.logger = Logger("MemberServiceLogger")

    def validate_member_data(self, df):
        """
               Validates the member data from a DataFrame.

               Args:
                   df (DataFrame): The DataFrame containing member data.

               Returns:
                   tuple: A tuple containing a list of valid members and a list of failed members.
        """

        members = []
        failed_members=[]
        headers = ["name", "surname", "booking_count", "date_joined"]
        for _, row in df.iterrows():
            try:
                # all required headers validation
                for head in headers:
                    if head not in row:
                        raise KeyError("Column missing")

                # Data type validation
                row["booking_count"] = int(row["booking_count"])
                row["date_joined"] = datetime.strptime(row["date_joined"], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                self.logger.error(msg="Invalid data format for user: " + str(row["name"]) +" and row no:" + str(_))
                failed_members.append(row.to_dict())
                continue
            except Exception as ex:
                self.logger.error(msg="Header missing in the row no:" + str(_) +" due to: " + str(ex)[:20])
                failed_members.append(row.to_dict())
                continue
            member = DbMember(name=row["name"], surname=row["surname"], booking_count=row["booking_count"],
                              date_joined=row["date_joined"])
            members.append(member)
        return members, failed_members

    async def add_members(self, file: UploadFile,bulk_update, db:Session,async_db:AsyncSession):
        """
                Adds members from an uploaded CSV file.

                Args:
                    file (UploadFile): The uploaded CSV file containing member data.
                    bulk_update (bool): Flag indicating whether to perform a bulk update.
                    db (Session): The database session.
                    async_db (AsyncSession): The asynchronous database session.

                Returns:
                    list: A list of invalid rows.
        """

        df, invalid_rows = await validate_csv_return_dataframe(file,"member")
        members,failed_members = self.validate_member_data(df)
        invalid_rows.extend(failed_members)
        if bulk_update:
            await self.member_repo.add_members_bulk(members,db,invalid_rows)
        else:
            await self.member_repo.add_member_synchronously(members,db,invalid_rows)
        results = list(filter(lambda elem: elem is not None, invalid_rows))
        return results

        # tasks=[]
        # async with db as session:
        #     for mem in members:
        #         tasks.append(self.member_repo.add_single_member(mem,session))
        # results = await asyncio.gather(*tasks)
        # results = list(filter(lambda elem: elem is not None, results))
        # results.extend(invalid_rows)
        # results.extend(failed_members)
        # return results

    async def get_all_members(self, db: Session):
        return await self.member_repo.get_all_members(db)


