from fastapi import APIRouter, Body, HTTPException, Depends, Request,Response, File, UploadFile,Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from typing import Dict
from app.models.schemas import User
from app.services.user import add_user, get_user_by_email
from app.services.record import get_record_by_master,add_record
from database.settings import doc_orders
from datetime import datetime, timedelta
from middleware.user_middleware import get_current_user
from fastapi.templating import Jinja2Templates
import jwt
import os


SECRET_KEY = os.environ.get("SECRET_KEY") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24

api_router: APIRouter = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@api_router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@api_router.post("/register", response_model=User)
async def register_user(body: Dict[str, str] = Body(...)):
    email: str = body.get("email")
    password: str = body.get("password")

    if not email or not password:
        return JSONResponse(content={"result": 400, "data": "Неверный формат данных."}, status_code=400)

    try:
        existing_user = await get_user_by_email(email)  
        if existing_user:
            return JSONResponse(content={"result": 400, "data": "Пользователь с таким email уже существует."}, status_code=400)
        
        user = await add_user(email=email, password=password)
        return JSONResponse(content={"result": 201, "user": user}, status_code=201)
    except Exception as e:  
        print(e)
        return JSONResponse(content={"result": 500, "data": "Произошла ошибка."}, status_code=500)


@api_router.post("/login")
async def login_user(body: Dict[str, str] = Body(...)):
    email: str = body.get("email")
    password: str = body.get("password")

    if not email or not password:
        return JSONResponse(content={"result": 400, "data": "Неверный формат данных."}, status_code=400)

    user = await get_user_by_email(email)
    if not user:
        return JSONResponse(content={"result": 404, "data": "Пользователь не найден."}, status_code=404)

    
    if not bcrypt.verify(password, user["password"]):
        return JSONResponse(content={"result": 400, "data": "Неверный пароль."}, status_code=400)

    
    access_token = create_access_token(data={"sub": user["email"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    return JSONResponse(content={"result": 200, "access_token": access_token, "token_type": "bearer"}, status_code=200)


@api_router.get("/protected")
async def read_protected_data(request: Request, current_user: dict = Depends(get_current_user)):
    # Рендер защищенного шаблона с данными пользователя
    return templates.TemplateResponse("protected.html", {"request": request, "user": current_user})


@api_router.post("/logout")
async def logout(response: Response):
    
    response.delete_cookie("token")
    return {"message": "Вы успешно вышли из системы"}


@api_router.get("/book")
async def book_record(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("book.html", {"request": request, "user": current_user})


@api_router.post("/api/record")
async def api_record(
    request: Request,
    user_id: str = Form(...),
    master: str = Form(...),
    created_at: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...)
):
    
    print({
        "user_id": user_id,
        "master": master,
        "created_at": created_at,
        "category": category,
        "price": price,
        "filename": file.filename
    })

    
    if not all([user_id, master, created_at, category, price]):
        raise HTTPException(status_code=400, detail="Не все данные предоставлены.")

    
    try:
        file_content = await file.read()
        
        with open(f"app/uploads/{file.filename}", "wb") as f:
            f.write(file_content)
        
        
        record = await add_record(user_id=user_id, master=master,
                                  category=category, price=price, filename=file.filename)
        
        return {"request": str(request), "record": record, "filename": file.filename}
    
    except Exception as e:
        print(f"Ошибка при создании записи: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при создании записи.")



@api_router.get("/main")
async def main_page(request: Request, current_user: dict = Depends(get_current_user)):

    return templates.TemplateResponse("main.html", {"request": request, "user": current_user})


@api_router.get("/myoffice")
async def my_office(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("office.html", {"request": request, "user": current_user})
    

@api_router.get("/api/orders")
async def get_user_orders(user_id: str, current_user: dict = Depends(get_current_user)):
    """
    Получить заказы пользователя по его user_id.
    """
    try:
        orders = await doc_orders.find({"user_id": user_id}).to_list(length=None)
        
        
        if not orders:
            return {"result": "Нет заказов для этого пользователя"}
        
        for order in orders:
            order["_id"] = str(order["_id"])
        
        return orders
    
    except Exception as e:
        print(f"Ошибка при получении заказов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при получении заказов.")



@api_router.get("/auth")
async def get_user_info(email: str):
    user = await doc_orders.find_one({"email": email})
    
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден.")
    
    user["_id"] = str(user["_id"])
    return {"user": user}
