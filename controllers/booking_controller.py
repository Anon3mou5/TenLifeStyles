
from fastapi import APIRouter, Depends,  status
from sqlalchemy.orm import Session

from configuration.database_config import get_db
from dto.base_dto import BaseDTO


from dto.booking_dto import ItemCancelRequest, ItemBookRequestBody
from models.db_bookings import DbBooking
from schemas.bookings import BookingBase
from services.auth_service import AuthService
from services.booking_service import BookingService
from utils.exceptions import  MemberNotFoundException, \
    MemberExhaustedLimitException, ItemNotFoundException, ItemDepletedException, ItemExpiredException, \
    BookingNotFoundException

auth_service:AuthService = AuthService()

router = APIRouter(
  tags=['bookings'],
    dependencies=[Depends(auth_service.validate_token)]
)

@router.post("/book", response_model=BaseDTO)
async def book_inventory(request:ItemBookRequestBody, db:Session = Depends(get_db)):
    booking_service = BookingService()
    try:
        booking_elem = await booking_service.book_an_item(request, db)
        order:BookingBase = BookingBase.model_validate(booking_elem)
        return BaseDTO(data=order)

    except MemberNotFoundException as ex:
        return BaseDTO(status=status.HTTP_404_NOT_FOUND, message=str(ex))

    except ItemNotFoundException as ex:
        return BaseDTO(status=status.HTTP_404_NOT_FOUND, message=str(ex))

    except ItemDepletedException as ex:
        return BaseDTO(status=status.HTTP_406_NOT_ACCEPTABLE, message=str(ex))

    except MemberExhaustedLimitException as ex:
        return BaseDTO(status=status.HTTP_406_NOT_ACCEPTABLE, message=str(ex))

    except ItemExpiredException as ex:
        return BaseDTO(status=status.HTTP_412_PRECONDITION_FAILED, message=str(ex))

    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while booking an item due to: " + str(ex))


@router.post("/cancel", response_model=BaseDTO)
async def cancel_booking(request:ItemCancelRequest,db:Session = Depends(get_db)):
    booking_service = BookingService()
    try:
        await booking_service.cancel_booking(request,db)
        return BaseDTO(data="Successfully cancelled booking")

    except MemberNotFoundException as ex:
        return BaseDTO(status=status.HTTP_404_NOT_FOUND, message=str(ex))

    except BookingNotFoundException as ex:
        return BaseDTO(status=status.HTTP_404_NOT_FOUND, message=str(ex))

    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while cancelling a booking due to: " + str(ex))

@router.get("/all", response_model=BaseDTO)
async def view_all_bookings(db:Session = Depends(get_db)):
    booking_service = BookingService()
    try:
        bookings = await booking_service.view_all_bookings(db)
        all_bookings = [BookingBase.model_validate(booking) for booking in bookings]
        return BaseDTO(data=all_bookings)

    except MemberNotFoundException as ex:
        return BaseDTO(status=status.HTTP_404_NOT_FOUND, message=str(ex))

    except BookingNotFoundException as ex:
        return BaseDTO(status=status.HTTP_404_NOT_FOUND, message=str(ex))

    except Exception as ex:
        return BaseDTO(status=500, message="Some issue occurred while cancelling a booking due to: " + str(ex))


