import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class BaseDTO(BaseModel):
    status: int = 200
    message : str = "successful"
    timestamp: str = datetime.datetime.now()
    data : Optional[Any] = None
