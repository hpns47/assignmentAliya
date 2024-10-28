from database.settings import doc_orders
from datetime import datetime
from bson.objectid import ObjectId
from passlib.hash import bcrypt
import fastapi

async def add_user(email: str, password: str) -> dict:
    
    hashed_password = bcrypt.hash(password)
    user: dict = {
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat()  
    }
    
    try:
        inserted_user = await doc_orders.insert_one(user)
        doc_order: dict = await doc_orders.find_one({"_id": inserted_user.inserted_id})
        
        
        doc_order["_id"] = str(doc_order["_id"])
        return doc_order
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
        return {}

async def get_user_by_email(email: str) -> dict:
    try:
        existing_user = await doc_orders.find_one({"email": email})
        if existing_user:
            existing_user["_id"] = str(existing_user["_id"]) 
        return existing_user
    except Exception as e:
        print(f"Ошибка при поиске пользователя: {e}")
        return {}
