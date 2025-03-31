from pydantic import BaseModel, Field
from typing import Optional, Any


class Success_Response_Schema(BaseModel):
    status: Optional[str] = "Success"
    message: Optional[str] = "Request Success"
    data: Optional[Any] = None


class Error_Response_Schema(BaseModel):
    status: Optional[str] = "Error"
    message: Optional[str] = "Error Occured"
    details: Optional[Any] = None


class Index_Response(BaseModel):
    message: str = Field(..., description="Welcome Message")
