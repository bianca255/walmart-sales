"""MySQL connection helper for the walmart_sales database (Task 2 schema).
Uses plain pymysql (no ORM) since the schema is fixed and small -
raw SQL keeps the CRUD logic simple and easy to explain in your report.
"""
import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "walmart_sales")


def get_connection():
    """Open a new MySQL connection. Caller is responsible for closing it."""
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=DictCursor,
        autocommit=False,
    )
