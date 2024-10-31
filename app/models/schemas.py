from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class User(BaseModel):
    _id : UUID
    email : str
    password : str
    created_at: datetime


class Record(BaseModel):
    _id: UUID
    user_id: str
    master: str
    created_at: datetime
    category: str
    price: float
    
    