from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class User(BaseModel):
    _id : UUID
    email : str
    password : str
    created_at: datetime
    
    