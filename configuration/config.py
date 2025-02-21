# Constants
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
ASYNC_DATABASE_URL = os.environ.get("DATABASE_URL")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MAX_BOOKINGS = 2
SECRET_KEY = os.environ.get("SECRET_KEY")
