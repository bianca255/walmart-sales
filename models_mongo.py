from typing import Optional
from pydantic import BaseModel


class SalesDocCreate(BaseModel):
    Store: int
    Dept: int
    Date: str
    Weekly_Sales: float
    IsHoliday_x: bool = False
    Type: Optional[str] = None
    Size: Optional[int] = None
    Temperature: Optional[float] = None
    Fuel_Price: Optional[float] = None
    MarkDown1: Optional[float] = None
    MarkDown2: Optional[float] = None
    MarkDown3: Optional[float] = None
    MarkDown4: Optional[float] = None
    MarkDown5: Optional[float] = None
    CPI: Optional[float] = None
    Unemployment: Optional[float] = None


class SalesDocUpdate(BaseModel):
    """PUT body - all fields optional, only provided fields get updated."""
    Weekly_Sales: Optional[float] = None
    IsHoliday_x: Optional[bool] = None
    Type: Optional[str] = None
    Size: Optional[int] = None
    Temperature: Optional[float] = None
    Fuel_Price: Optional[float] = None
    MarkDown1: Optional[float] = None
    MarkDown2: Optional[float] = None
    MarkDown3: Optional[float] = None
    MarkDown4: Optional[float] = None
    MarkDown5: Optional[float] = None
    CPI: Optional[float] = None
    Unemployment: Optional[float] = None
