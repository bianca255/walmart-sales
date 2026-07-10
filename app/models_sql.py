from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class TrainSalesCreate(BaseModel):
    Store: int
    Dept: int
    Date: date
    Weekly_Sales: Decimal
    IsHoliday: bool = False


class TrainSalesUpdate(BaseModel):
    """PUT body - Weekly_Sales / IsHoliday are the only editable fields.
    Store, Dept, Date form the primary key and are taken from the URL."""
    Weekly_Sales: Optional[Decimal] = None
    IsHoliday: Optional[bool] = None


class TrainSalesOut(BaseModel):
    Store: int
    Dept: int
    Date: date
    Weekly_Sales: Decimal
    IsHoliday: bool
