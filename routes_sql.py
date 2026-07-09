"""CRUD + time-series endpoints for the MySQL `TrainSales` table
(the fact table in the Task 2 schema: Store, Dept, Date, Weekly_Sales, IsHoliday).
"""
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from pymysql.err import IntegrityError

from database import get_connection
from models_sql import TrainSalesCreate, TrainSalesUpdate, TrainSalesOut

router = APIRouter(prefix="/sql/sales", tags=["MySQL - TrainSales"])

@router.get("/latest", response_model=TrainSalesOut)
def get_latest_record():
    """Return the single most recent Weekly_Sales record by Date."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT Store, Dept, Date, Weekly_Sales, IsHoliday "
                "FROM TrainSales ORDER BY Date DESC LIMIT 1"
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No records found")
        return row
    finally:
        conn.close()


@router.get("/range", response_model=list[TrainSalesOut])
def get_records_by_date_range(
    start: date = Query(..., description="Start date, e.g. 2012-01-01"),
    end: date = Query(..., description="End date, e.g. 2012-01-31"),
    store: int | None = Query(None, description="Optional store filter"),
    limit: int = Query(500, le=5000),
):
    """Return records whose Date falls within [start, end], optionally filtered by store."""
    if start > end:
        raise HTTPException(status_code=400, detail="start must be <= end")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if store is not None:
                cur.execute(
                    "SELECT Store, Dept, Date, Weekly_Sales, IsHoliday FROM TrainSales "
                    "WHERE Date BETWEEN %s AND %s AND Store = %s "
                    "ORDER BY Date ASC LIMIT %s",
                    (start, end, store, limit),
                )
            else:
                cur.execute(
                    "SELECT Store, Dept, Date, Weekly_Sales, IsHoliday FROM TrainSales "
                    "WHERE Date BETWEEN %s AND %s "
                    "ORDER BY Date ASC LIMIT %s",
                    (start, end, limit),
                )
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()

@router.post("", response_model=TrainSalesOut, status_code=201)
def create_record(record: TrainSalesCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO TrainSales (Store, Dept, Date, Weekly_Sales, IsHoliday) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (record.Store, record.Dept, record.Date,
                     record.Weekly_Sales, int(record.IsHoliday)),
                )
                conn.commit()
            except IntegrityError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=409,
                    detail=f"Record already exists or Store not found: {e}",
                )
        return record.model_dump()
    finally:
        conn.close()


@router.get("", response_model=list[TrainSalesOut])
def list_records(
    store: int | None = None,
    dept: int | None = None,
    limit: int = Query(100, le=5000),
    offset: int = 0,
):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT Store, Dept, Date, Weekly_Sales, IsHoliday FROM TrainSales WHERE 1=1"
            params = []
            if store is not None:
                sql += " AND Store = %s"
                params.append(store)
            if dept is not None:
                sql += " AND Dept = %s"
                params.append(dept)
            sql += " ORDER BY Date DESC LIMIT %s OFFSET %s"
            params += [limit, offset]
            cur.execute(sql, params)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


@router.get("/{store}/{dept}/{sale_date}", response_model=TrainSalesOut)
def get_record(store: int, dept: int, sale_date: date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT Store, Dept, Date, Weekly_Sales, IsHoliday FROM TrainSales "
                "WHERE Store = %s AND Dept = %s AND Date = %s",
                (store, dept, sale_date),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Record not found")
        return row
    finally:
        conn.close()


@router.put("/{store}/{dept}/{sale_date}", response_model=TrainSalesOut)
def update_record(store: int, dept: int, sale_date: date, update: TrainSalesUpdate):
    fields, params = [], []
    if update.Weekly_Sales is not None:
        fields.append("Weekly_Sales = %s")
        params.append(update.Weekly_Sales)
    if update.IsHoliday is not None:
        fields.append("IsHoliday = %s")
        params.append(int(update.IsHoliday))

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            params += [store, dept, sale_date]
            cur.execute(
                f"UPDATE TrainSales SET {', '.join(fields)} "
                "WHERE Store = %s AND Dept = %s AND Date = %s",
                params,
            )
            if cur.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Record not found")
            conn.commit()

            cur.execute(
                "SELECT Store, Dept, Date, Weekly_Sales, IsHoliday FROM TrainSales "
                "WHERE Store = %s AND Dept = %s AND Date = %s",
                (store, dept, sale_date),
            )
            return cur.fetchone()
    finally:
        conn.close()


@router.delete("/{store}/{dept}/{sale_date}", status_code=204)
def delete_record(store: int, dept: int, sale_date: date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM TrainSales WHERE Store = %s AND Dept = %s AND Date = %s",
                (store, dept, sale_date),
            )
            if cur.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Record not found")
            conn.commit()
        return None
    finally:
        conn.close()
