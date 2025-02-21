from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from configuration.database_config import get_db
from dto.auth_dto import AuthenticationCreationRequestBody
from dto.base_dto import BaseDTO
from models.db_user import DbUser
from schemas.user import UserBase
from services.auth_service import AuthService
from utils.exceptions import UserNotFoundException, InvalidUserException


router = APIRouter(
  tags=['authentication']
)

@router.post('/login', response_model=BaseDTO)
def generate_token(request: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    auth_service = AuthService()
    try:
        access_token,user = auth_service.validate_user_and_generate_token(request,db)
    except InvalidUserException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid user')
    except Exception as ex:
        return BaseDTO(status=500,message="Some issue occurred while getting access token due to: " +str(ex))

    data =  {
    'access_token': access_token,
    'token_type': 'bearer',
    'user_id': user.id,
    'username': user.username,
        }

    return BaseDTO(data=data)

@router.post('/create', response_model=BaseDTO)
def create_an_account(request : AuthenticationCreationRequestBody,db:Session = Depends(get_db)):
    try:
        auth_service = AuthService()
        user:UserBase = UserBase.model_validate(auth_service.create_user(request,db))
        return BaseDTO(data=user)
    except Exception as ex:
        return BaseDTO(status=500,message="Some issue occurred while creating an account due to: " +str(ex))

