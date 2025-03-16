from fastapi import FastAPI, HTTPException, Request,status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from shared import response_schema
import settings as app_settings
from database import engine,Base
from shared import response_schema
from shared.generic_error_handling import Generic_Error_Handling

from modules.users.controller import users_router
Base.metadata.create_all(bind=engine) # To autocreate SQL Tables


app = FastAPI(title=app_settings.settings.APP_NAME)

#  Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],  # Allow all origins (Not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Entry_Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        
        try:
            response =  await call_next(request)
            
            if isinstance(response, JSONResponse):
                # Only attempt model_dump if the response is a Pydantic model
                if hasattr(response, 'model_dump'):
                    return response_schema.Success_Response_Schema(**response.model_dump())

           
            return response
        
        except SQLAlchemyError as e:
            
            error_details = Generic_Error_Handling.db_exception_handling(e)
            
            return JSONResponse(
                status_code=500,
                content=response_schema.Error_Response_Schema(details=error_details).model_dump()
            )

app.add_middleware(Entry_Middleware)

app.include_router(router = users_router , prefix="/users" , tags = ["users"])


@app.get("/")
async def read_root():
    return response_schema.Index_Response(message = "Welcome Guys")
