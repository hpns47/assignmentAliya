from database.settings import doc_orders
from datetime import datetime


async def add_record(user_id: str, master: str, category: str, price: float, filename: str) -> dict:
    
    
    record: dict = {
        "user_id": user_id,
        "master": master,
        "created_at": datetime.utcnow().isoformat(),
        "category": category,
        "price": price,
        "file_name": filename

    }
    
    
    try:
        inserted_record = await doc_orders.insert_one(record)
        doc_order: dict = await doc_orders.find_one({"_id": inserted_record.inserted_id})
        
        
        doc_order["_id"] = str(doc_order["_id"])
        return doc_order
    except Exception as e:
        print(f"Ошибка при добавлении записи: {e}")
        return {}


async def get_record_by_master(master: str) -> dict:
    try:
        existing_record = await doc_orders.find_one({"master": master})
        if existing_record:
            existing_record["_id"] = str(existing_record["_id"]) 
        return existing_record
    except Exception as e:
        print(f"Ошибка при поиске пользователя: {e}")
        return {}
