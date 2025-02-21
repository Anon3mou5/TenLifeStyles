from fastapi import APIRouter, Depends,UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from configuration.database_config import get_db
from dto.base_dto import BaseDTO
from schemas.member import MemberBase

from services.auth_service import AuthService
from services.member_service import MemberService

auth_service:AuthService = AuthService()

router = APIRouter(
  tags=['member'],
  dependencies=[Depends(auth_service.validate_token)]
)

@router.get("/all-members", response_model=BaseDTO)
async def get_all_members(db: Session = Depends(get_db)):
    member_service = MemberService()
    try:
        members = await member_service.get_all_members(db)
        all_members = [MemberBase.model_validate(member) for member in members]
        return BaseDTO(data=all_members)
    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while fetching members due to: " + str(ex))


@router.post("/upload-members", response_model=BaseDTO)
async def upload_members(bulk_update:bool, file: UploadFile = File(...),db:Session = Depends(get_db)):
    member_service = MemberService()
    try:
        failed_rows = await member_service.add_members(file,bulk_update, db)
        if failed_rows and len(failed_rows)>0:
            return BaseDTO(status=206, message="partial data insertion successful, failed information is attached",data=failed_rows)

        return BaseDTO(data="added all members successfully")

    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while bulk uploading members due to: " + str(ex))
