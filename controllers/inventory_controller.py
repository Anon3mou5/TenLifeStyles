
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from configuration.database_config import get_db, get_async_db
from dto.base_dto import BaseDTO
from schemas.inventory import InventoryBase
from services.auth_service import AuthService
from services.inventory_service import InventoryService

auth_service:AuthService = AuthService()

router = APIRouter(
  tags=['inventory'],
# dependencies=[Depends(auth_service.validate_token)]
)

@router.post("/upload-inventories", response_model=BaseDTO)
async def upload_members(bulk_update:bool, file: UploadFile = File(...), db:Session = Depends(get_db)):
    inventory_service = InventoryService()
    try:
        failed_rows = await inventory_service.add_inventories(file,bulk_update,db)
        if failed_rows and len(failed_rows) > 0:
            return BaseDTO(status=206, message="partial data insertion successful, failed information is attached",
                           data=failed_rows)
        return BaseDTO(data="added all inventories successfully")

    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while bulk uploading inventories due to: " + str(ex))

@router.get("/view-all", response_model=BaseDTO)
async def get_all_inventories(db: Session = Depends(get_db)):
    inventory_service = InventoryService()
    try:
        inventories = await inventory_service.get_all_inventories(db)
        all_inventories = [InventoryBase.model_validate(inventory) for inventory in inventories]
        return BaseDTO(data=all_inventories)
    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while fetching inventories due to: " + str(ex))


