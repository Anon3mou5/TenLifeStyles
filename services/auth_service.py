from datetime import timedelta, datetime
from fastapi import HTTPException, status
from typing import Optional, List, Union

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from requests import Session

from configuration.config import SECRET_KEY, ALGORITHM
from configuration.database_config import get_db
from dto.auth_dto import AuthenticationCreationRequestBody
from models.db_user import DbUser
from repositories.user_repo import UserRepository
from utils.exceptions import UserNotFoundException, InvalidUserException
from utils.hash import Hash
from utils.utilities import Singleton

outh2_scheme = OAuth2PasswordBearer(tokenUrl='login')

class AuthService(metaclass=Singleton):

    jwt_bearer = HTTPBearer()

    def __init__(self):
        """
              Initialize the AuthService with optional headers.

              :param headers: Optional dictionary of headers.
        """
        self.user_repo = UserRepository()


    def create_access_token(self,data: dict, expires_delta: Optional[timedelta] = None):
        """
                Create a JWT access token.

                :param data: Dictionary containing the data to encode in the token.
                :param expires_delta: Optional timedelta for token expiration.
                :return: Encoded JWT token.

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def validate_user_and_generate_token(self,request: OAuth2PasswordRequestForm,db:Session) -> List[Union[str,DbUser]]:
        """
                Validate the user and generate a JWT token.

                :param request: OAuth2PasswordRequestForm containing the user credentials.
                :param db: Database session.
                :return: List containing the JWT token and the user object.
                :raises UserNotFoundException: If the user is not found.
                :raises InvalidUserException: If the user credentials are invalid.
        """
        user = self.user_repo.get_user(username=request.username,db=db)
        if not user:
            raise UserNotFoundException
        if not Hash.verify(user.password, request.password):
            raise InvalidUserException

        return [self.create_access_token(data = {'username': user.username}),user]


    def create_user(self,request : AuthenticationCreationRequestBody,db:Session) -> DbUser:
        """
                Create a new user.

                :param request: AuthenticationCreationRequestBody containing the user details.
                :param db: Database session.
                :return: The created user object.
        """
        return self.user_repo.create_user(request,db)


    def validate_token(self,token: HTTPAuthorizationCredentials = Depends(jwt_bearer),db:Session=Depends(get_db)):
        """
               Validate the JWT token.

               :param token: HTTPAuthorizationCredentials containing the token.
               :param db: Database session.
               :return: The user object if the token is valid.
               :raises HTTPException: If the token is invalid or the user is not found.
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("username")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.user_repo.get_user(username=username,db=db)

        if user is None:
            raise credentials_exception

        return user

