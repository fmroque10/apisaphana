from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection


app = FastAPI(
    title="SAP HANA Sales Analytics API",
    description="REST API for SAP HANA SALES_TIME_SERIES analytics",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.40.131:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/health")
def health():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1 FROM DUMMY")
        row = cursor.fetchone()

        database_name = row[0]

        return {
            "status": "ok",
            "hana": "connected",
            "database": database_name
        }

    except Exception as e:
        return {
            "status": "error",
            "hana": "connection_failed",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# ORIGINAL SALES ENDPOINT
# DO NOT MODIFY
# ---------------------------------------------------------

@app.get("/sales")
def get_sales():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                ID,
                MONTH,
                YEAR,
                PRODUCTID,
                CLIENTID,
                QUANTITY,
                PROFIT
            FROM SALES_TIME_SERIES
            ORDER BY YEAR, MONTH, ID
        """)

        rows = cursor.fetchall()

        sales = []

        for row in rows:
            sales.append({
                "ID": row[0],
                "MONTH": row[1],
                "YEAR": row[2],
                "PRODUCTID": row[3],
                "CLIENTID": row[4],
                "QUANTITY": row[5],
                "PROFIT": float(row[6])
            })

        return {
            "count": len(sales),
            "data": sales
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# NEW PAGINATED SALES ENDPOINT
# ---------------------------------------------------------

@app.get("/sales/paginated")
def get_sales_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500)
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # Get total number of records
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM SALES_TIME_SERIES
        """)

        total_records = cursor.fetchone()[0]

        # -------------------------------------------------
        # Calculate OFFSET
        # -------------------------------------------------

        offset = (page - 1) * limit

        # -------------------------------------------------
        # Get only the requested page
        # -------------------------------------------------

        cursor.execute(f"""
            SELECT
                ID,
                MONTH,
                YEAR,
                PRODUCTID,
                CLIENTID,
                QUANTITY,
                PROFIT
            FROM SALES_TIME_SERIES
            ORDER BY YEAR, MONTH, ID
            LIMIT {limit}
            OFFSET {offset}
        """)

        rows = cursor.fetchall()

        sales = []

        for row in rows:
            sales.append({
                "ID": row[0],
                "MONTH": row[1],
                "YEAR": row[2],
                "PRODUCTID": row[3],
                "CLIENTID": row[4],
                "QUANTITY": row[5],
                "PROFIT": float(row[6])
            })

        # -------------------------------------------------
        # Calculate total number of pages
        # -------------------------------------------------

        total_pages = (total_records + limit - 1) // limit

        return {
            "page": page,
            "limit": limit,
            "total": total_records,
            "pages": total_pages,
            "count": len(sales),
            "data": sales
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# TIME SERIES
# ---------------------------------------------------------

@app.get("/sales/timeseries")
def get_sales_timeseries():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                YEAR,
                MONTH,
                SUM(QUANTITY) AS QUANTITY,
                SUM(PROFIT) AS PROFIT
            FROM SALES_TIME_SERIES
            GROUP BY YEAR, MONTH
            ORDER BY YEAR, MONTH
        """)

        rows = cursor.fetchall()

        timeseries = []

        for row in rows:
            timeseries.append({
                "YEAR": row[0],
                "MONTH": row[1],
                "QUANTITY": row[2],
                "PROFIT": float(row[3])
            })

        return {
            "count": len(timeseries),
            "data": timeseries
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# SALES BY PRODUCT
# ---------------------------------------------------------

@app.get("/sales/by-product")
def get_sales_by_product():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                YEAR,
                MONTH,
                PRODUCTID,
                SUM(QUANTITY) AS QUANTITY,
                SUM(PROFIT) AS PROFIT
            FROM SALES_TIME_SERIES
            GROUP BY YEAR, MONTH, PRODUCTID
            ORDER BY YEAR, MONTH, PRODUCTID
        """)

        rows = cursor.fetchall()

        product_sales = []

        for row in rows:
            product_sales.append({
                "YEAR": row[0],
                "MONTH": row[1],
                "PRODUCTID": row[2],
                "QUANTITY": row[3],
                "PROFIT": float(row[4])
            })

        return {
            "count": len(product_sales),
            "data": product_sales
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# SALES BY CLIENT
# ---------------------------------------------------------

@app.get("/sales/by-client")
def get_sales_by_client():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                YEAR,
                MONTH,
                CLIENTID,
                SUM(QUANTITY) AS QUANTITY,
                SUM(PROFIT) AS PROFIT
            FROM SALES_TIME_SERIES
            GROUP BY YEAR, MONTH, CLIENTID
            ORDER BY YEAR, MONTH, CLIENTID
        """)

        rows = cursor.fetchall()

        client_sales = []

        for row in rows:
            client_sales.append({
                "YEAR": row[0],
                "MONTH": row[1],
                "CLIENTID": row[2],
                "QUANTITY": row[3],
                "PROFIT": float(row[4])
            })

        return {
            "count": len(client_sales),
            "data": client_sales
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()