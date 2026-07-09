"""
One-time data loader: reads walmart_cleaned_merged.csv and populates
both databases to match the Task 2 design.

MySQL   -> Stores, Features, TrainSales  (per schema.sql)
MongoDB -> sales collection (merged documents)

Usage:
    python load_data.py path/to/walmart_cleaned_merged.csv
"""
import sys
import pandas as pd
import pymysql
from pymongo import MongoClient

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "walmart_cleaned_merged.csv"

MYSQL_CONFIG = dict(
    host="localhost", port=3306, user="root",
    password="walmart123", database="walmart_sales",
)
MONGO_URI = "mongodb://localhost:27017"


def load_mysql(df: pd.DataFrame):
    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()

    # 1) Create schema (safe if already exists)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Stores (
            Store INT PRIMARY KEY,
            Type CHAR(1),
            Size INT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Features (
            Store INT NOT NULL,
            Date DATE NOT NULL,
            Temperature FLOAT,
            Fuel_Price FLOAT,
            MarkDown1 FLOAT, MarkDown2 FLOAT, MarkDown3 FLOAT,
            MarkDown4 FLOAT, MarkDown5 FLOAT,
            CPI FLOAT, Unemployment FLOAT, IsHoliday TINYINT,
            PRIMARY KEY (Store, Date),
            FOREIGN KEY (Store) REFERENCES Stores(Store)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TrainSales (
            Store INT NOT NULL, Dept INT NOT NULL, Date DATE NOT NULL,
            Weekly_Sales DECIMAL(12,2), IsHoliday TINYINT,
            PRIMARY KEY (Store, Dept, Date),
            FOREIGN KEY (Store) REFERENCES Stores(Store)
        )
    """)
    conn.commit()

    # 2) Stores (one row per unique store)
    stores = df[["Store", "Type", "Size"]].drop_duplicates(subset=["Store"])
    cur.executemany(
        "INSERT IGNORE INTO Stores (Store, Type, Size) VALUES (%s, %s, %s)",
        stores.values.tolist(),
    )
    conn.commit()
    print(f"Loaded {len(stores)} stores")

    # 3) Features (one row per Store+Date)
    feat_cols = ["Store", "Date", "Temperature", "Fuel_Price",
                 "MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4", "MarkDown5",
                 "CPI", "Unemployment", "IsHoliday"]
    features = df[feat_cols].drop_duplicates(subset=["Store", "Date"]).copy()
    features["IsHoliday"] = features["IsHoliday"].astype(bool).astype(int)
    cur.executemany(
        "INSERT IGNORE INTO Features (Store, Date, Temperature, Fuel_Price, "
        "MarkDown1, MarkDown2, MarkDown3, MarkDown4, MarkDown5, CPI, Unemployment, IsHoliday) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        features.values.tolist(),
    )
    conn.commit()
    print(f"Loaded {len(features)} feature rows")

    # 4) TrainSales
    sales_cols = ["Store", "Dept", "Date", "Weekly_Sales", "IsHoliday"]
    sales = df[sales_cols].copy()
    sales["IsHoliday"] = sales["IsHoliday"].astype(bool).astype(int)
    cur.executemany(
        "INSERT IGNORE INTO TrainSales (Store, Dept, Date, Weekly_Sales, IsHoliday) "
        "VALUES (%s,%s,%s,%s,%s)",
        sales.values.tolist(),
    )
    conn.commit()
    print(f"Loaded {len(sales)} sales rows")

    cur.close()
    conn.close()


def load_mongo(df: pd.DataFrame):
    client = MongoClient(MONGO_URI)
    coll = client["walmart_sales"]["sales"]

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df = df.rename(columns={"IsHoliday": "IsHoliday_x"})
    df["IsHoliday_x"] = df["IsHoliday_x"].astype(bool)

    records = df.to_dict(orient="records")
    coll.delete_many({})  # fresh load
    coll.insert_many(records)
    print(f"Loaded {len(records)} documents into MongoDB")


if __name__ == "__main__":
    print(f"Reading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    print(f"{len(df)} rows found")

    load_mysql(df)
    load_mongo(df)
    print("Done.")