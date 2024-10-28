from fastapi import FastAPI
from database.settings import  database, check_connection
from fastapi.staticfiles import StaticFiles

import yaml

from fastapi.middleware.cors import CORSMiddleware
DB_NAME: str = "assignment"

async def create_app() -> FastAPI:
    app = FastAPI(docs_url="/docs")
    
    origins = [
        "http://localhost:5002",
        
    ]

    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],  
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    try:
        await check_connection()
        
        if DB_NAME not in await database.list_collection_names():
            print("Collection 'carts' does not exist. Creating...")
            
            
            print("Collection 'carts' created.")
        else:
            print("Collection 'carts' already exists.")

    except Exception as e:
        print(f"Error initializing MongoDB: {e}")

    register_views(app=app)

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        app.openapi_schema = app.get_openapi()  
    
        
        
        
    # app.openapi = custom_openapi
    
    return app

def register_views(app: FastAPI):
    from app.controllers.views import api_router
    app.include_router(api_router)