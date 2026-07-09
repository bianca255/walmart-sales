# Walmart Sales Forecast — Task 3: CRUD & Time-Series Query Endpoints

FastAPI service exposing CRUD operations and the required time-series queries
(latest record, date-range) over both databases built in Task 2:

- **MySQL** `walmart_sales.TrainSales` (Store, Dept, Date, Weekly_Sales, IsHoliday)
- **MongoDB** `walmart_sales.sales` (merged Train + Stores + Features documents)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with your real MySQL password / Mongo URI
```

Make sure your Task 2 databases are already running and populated
(same MySQL server + `walmart_sales` DB, same MongoDB `sales` collection).

## Run

```bash
uvicorn main:app --reload
```

Interactive Swagger docs (test every endpoint from the browser, screenshot for
your report): **http://127.0.0.1:8000/docs**

## Endpoints

### MySQL — `/sql/sales`

| Method | Path                              | Description                          |
|--------|-----------------------------------|---------------------------------------|
| POST   | `/sql/sales`                      | Create a record                       |
| GET    | `/sql/sales`                      | List records (filter: `store`, `dept`)|
| GET    | `/sql/sales/latest`               | Most recent record by Date            |
| GET    | `/sql/sales/range?start=&end=`    | Records within a date range           |
| GET    | `/sql/sales/{store}/{dept}/{date}`| Get one record                        |
| PUT    | `/sql/sales/{store}/{dept}/{date}`| Update Weekly_Sales / IsHoliday       |
| DELETE | `/sql/sales/{store}/{dept}/{date}`| Delete a record                       |

### MongoDB — `/mongo/sales`

| Method | Path                            | Description                     |
|--------|----------------------------------|----------------------------------|
| POST   | `/mongo/sales`                   | Create a document                |
| GET    | `/mongo/sales`                   | List documents (filter: `store`, `dept`) |
| GET    | `/mongo/sales/latest`            | Most recent document by Date     |
| GET    | `/mongo/sales/range?start=&end=` | Documents within a date range    |
| GET    | `/mongo/sales/{doc_id}`          | Get one document by `_id`        |
| PUT    | `/mongo/sales/{doc_id}`          | Update a document                |
| DELETE | `/mongo/sales/{doc_id}`          | Delete a document                |

## Quick test examples

```bash
# Create a record (MySQL)
curl -X POST http://127.0.0.1:8000/sql/sales \
  -H "Content-Type: application/json" \
  -d '{"Store": 1, "Dept": 1, "Date": "2012-12-01", "Weekly_Sales": 30000.00, "IsHoliday": false}'

# Latest record (MySQL)
curl http://127.0.0.1:8000/sql/sales/latest

# Date range (MongoDB)
curl "http://127.0.0.1:8000/mongo/sales/range?start=2012-01-01&end=2012-01-31"
```

## Notes for the report

- `latest` and `range` routes are registered before the `/{id}`-style routes
  in both routers so FastAPI's path matcher doesn't mistake `"latest"` for a
  store id / document id.
- MySQL CRUD uses raw `pymysql` (no ORM) against the fixed Task 2 schema —
  keeps the SQL explicit and easy to map back to `schema.sql`.
- MongoDB CRUD uses `pymongo` directly against the `sales` collection;
  `_id` (ObjectId) is converted to a string in responses since FastAPI can't
  serialize ObjectId natively.
