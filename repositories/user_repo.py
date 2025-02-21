from typing import Optional, Type

from fastapi.params import Depends
from sqlalchemy.orm import Session

from configuration.database_config import get_db
from dto.auth_dto import AuthenticationCreationRequestBody
from models.db_user import DbUser
from utils.hash import Hash
from utils.utilities import Singleton


class UserRepository(metaclass=Singleton):

    def get_user(self, username:str,db:Session)-> Optional[Type[DbUser]]:
        return db.query(DbUser).filter(DbUser.username.like(username)).first()

    def create_user(self, request: AuthenticationCreationRequestBody,db:Session):
        new_user = DbUser(
            username=request.username,
            fullname=request.fullname,
            email=request.email,
            password=Hash.bcrypt(request.password))

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_all_users(self,db:Session):
        users = db.query(DbUser).all()
        return users




