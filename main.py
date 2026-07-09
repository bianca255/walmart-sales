from fastapi import FastAPI

from routes_sql import router as sql_router
from routes_mongo import router as mongo_router

app = FastAPI(
    title="Walmart Sales - Task 3 API",
    description="CRUD and time-series query endpoints over the MySQL "
                 "(TrainSales) and MongoDB (sales) stores built in Task 2.",
    version="1.0.0",
)

app.include_router(sql_router)
app.include_router(mongo_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "sql_endpoints": "/sql/sales",
        "mongo_endpoints": "/mongo/sales",
        "docs": "/docs",
    }