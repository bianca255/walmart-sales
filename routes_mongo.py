"""CRUD + time-series endpoints for the MongoDB `sales` collection
(Task 2 design: merged train/stores/features documents).
"""
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from bson.errors import InvalidId

from mongo_db import sales_collection
from models_mongo import SalesDocCreate, SalesDocUpdate

router = APIRouter(prefix="/mongo/sales", tags=["MongoDB - sales"])


def serialize(doc: dict) -> dict:
    """Convert Mongo's ObjectId to a plain string so FastAPI can JSON-encode it."""
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    return doc


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document id")

@router.get("/latest")
def get_latest_record():
    """Return the single most recent document by Date."""
    doc = sales_collection.find_one(sort=[("Date", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No records found")
    return serialize(doc)


@router.get("/range")
def get_records_by_date_range(
    start: date = Query(..., description="Start date, e.g. 2012-01-01"),
    end: date = Query(..., description="End date, e.g. 2012-01-31"),
    store: int | None = Query(None, description="Optional store filter"),
    limit: int = Query(500, le=5000),
):
    if start > end:
        raise HTTPException(status_code=400, detail="start must be <= end")

    query = {
        "Date": {
            "$gte": start.isoformat(),
            "$lte": end.isoformat(),
        }
    }
    if store is not None:
        query["Store"] = store

    docs = sales_collection.find(query).sort("Date", 1).limit(limit)
    return [serialize(d) for d in docs]

@router.post("", status_code=201)
def create_record(record: SalesDocCreate):
    result = sales_collection.insert_one(record.model_dump())
    created = sales_collection.find_one({"_id": result.inserted_id})
    return serialize(created)


@router.get("")
def list_records(
    store: int | None = None,
    dept: int | None = None,
    limit: int = Query(100, le=5000),
    skip: int = 0,
):
    query = {}
    if store is not None:
        query["Store"] = store
    if dept is not None:
        query["Dept"] = dept

    docs = sales_collection.find(query).sort("Date", -1).skip(skip).limit(limit)
    return [serialize(d) for d in docs]


@router.get("/{doc_id}")
def get_record(doc_id: str):
    doc = sales_collection.find_one({"_id": to_object_id(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Record not found")
    return serialize(doc)


@router.put("/{doc_id}")
def update_record(doc_id: str, update: SalesDocUpdate):
    fields = {k: v for k, v in update.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = sales_collection.update_one(
        {"_id": to_object_id(doc_id)}, {"$set": fields}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")

    doc = sales_collection.find_one({"_id": to_object_id(doc_id)})
    return serialize(doc)


@router.delete("/{doc_id}", status_code=204)
def delete_record(doc_id: str):
    result = sales_collection.delete_one({"_id": to_object_id(doc_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return None
