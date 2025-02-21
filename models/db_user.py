from sqlalchemy import UniqueConstraint, Column, Integer, String

from configuration.database_config import Base



class DbUser(Base):
    __tablename__ = 'users'
    __table_args__ = ( UniqueConstraint('username', 'email', name="uniquecol"),)
    id= Column( Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    fullname = Column(String)
    email = Column(String, nullable=True)
    password = Column(String)




