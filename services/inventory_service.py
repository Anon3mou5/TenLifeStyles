import asyncio
import csv
from datetime import datetime
from logging import Logger

from fastapi import UploadFile
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models.db_inventory import DbInventory
from models.db_member import DbMember
from repositories.inventory_repo import InventoryRepo
from utils.exceptions import InvalidFileException
from utils.utilities import Singleton, validate_csv_return_dataframe


class InventoryService(metaclass=Singleton):
    """
       Service class for handling inventory operations.
       Utilizes Singleton pattern to ensure a single instance.
    """
    def __init__(self):
        """
                Initializes the InventoryService with an inventory repository and a logger.
        """
        self.inventory_repo = InventoryRepo()
        self.logger = Logger("InventoryService")

    def validate_inventory_data(self, df):
        """
               Validates the inventory data from a DataFrame.

               Args:
                   df (DataFrame): The DataFrame containing inventory data.

               Returns:
                   tuple: A tuple containing a list of valid inventories and a list of failed items.
        """

        inventories = []
        failed_items = []
        headers=["title","description","remaining_count","expiration_date"]
        for _, row in df.iterrows():
            try:
                #all required headers validation
                for head in headers:
                    if head not in row:
                        raise KeyError("Column missing")

                #Data type validation
                row["remaining_count"] = int(row["remaining_count"])
                row["expiration_date"] = datetime.strptime(row["expiration_date"], "%d/%m/%Y")
            except ValueError:
                self.logger.info(msg="Invalid data format for item: " + str(row["title"]) + " and row no:" + str(_))
                failed_items.append(row.to_dict())
                continue
            except Exception as ex:
                self.logger.error(msg="Header missing in the row no:" + str(_) +" due to: " + str(ex)[:20])
                failed_items.append(row.to_dict())
                continue
            inventory = DbInventory(title=row["title"], description=row["description"], remaining_count=row["remaining_count"],
                                    expiration_date=row["expiration_date"])
            inventories.append(inventory)
        return inventories,failed_items

    async def add_inventories(self, file: UploadFile,bulk_update, db:Session):
        """
                Adds inventories from an uploaded CSV file.

                Args:
                    file (UploadFile): The uploaded CSV file containing inventory data.
                    bulk_update (bool): Flag indicating whether to perform a bulk update.
                    db (Session): The database session.

                Returns:
                    list: A list of invalid rows.
        """

        df,invalid_rows = await validate_csv_return_dataframe(file,"inventory")
        inventories,failed_items= self.validate_inventory_data(df)
        invalid_rows.extend(failed_items)
        if bulk_update:
            await self.inventory_repo.add_inventory_bulk(inventories,db,invalid_rows)
        else:
            await self.inventory_repo.add_inventory_synchronously(inventories,db,invalid_rows)
        results = list(filter(lambda elem: elem is not None, invalid_rows))
        return results

        # tasks = []
        # async with db as session:
        #     for inv in inventories:
        #         tasks.append(self.inventory_repo.add_single_item(inv, session))
        # results = await asyncio.gather(*tasks)
        # results = list(filter(lambda elem: elem is not None, results))
        # results.extend(invalid_rows)
        # results.extend(failed_items)
        # return results

    async def get_all_inventories(self, db: Session):
        return await self.inventory_repo.get_all_inventories(db)

