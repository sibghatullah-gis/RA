"""
All reads/writes to Postgres for the app go through these functions.
Keeping this separate from app.py means the Streamlit UI code never
touches SQL directly.
"""
import pandas as pd
from sqlalchemy import text
from db_conn import get_engine

DELIVERABLE_COLS = [
    "year", "division", "unit", "pillar_wp", "country", "topic",
    "output_type", "delivery_date", "status", "focal_point",
]
REQUEST_COLS = [
    "country", "status", "topic", "division", "focal_point",
    "output", "source_of_request", "date_received", "date_delivered",
]


def fetch_deliverables() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM deliverables ORDER BY id", engine)


def fetch_requests() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM requests ORDER BY id", engine)


def insert_deliverable(row: dict):
    engine = get_engine()
    cols = [c for c in DELIVERABLE_COLS if c in row]
    placeholders = ", ".join(f":{c}" for c in cols)
    with engine.begin() as conn:
        conn.execute(
            text(f"INSERT INTO deliverables ({', '.join(cols)}) VALUES ({placeholders})"),
            {c: row.get(c) for c in cols},
        )


def update_deliverable(row_id: int, row: dict):
    engine = get_engine()
    cols = [c for c in DELIVERABLE_COLS if c in row]
    set_clause = ", ".join(f"{c} = :{c}" for c in cols)
    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE deliverables SET {set_clause}, updated_at = now() WHERE id = :id"),
            {**{c: row.get(c) for c in cols}, "id": row_id},
        )


def delete_deliverable(row_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM deliverables WHERE id = :id"), {"id": row_id})


def insert_request(row: dict):
    engine = get_engine()
    cols = [c for c in REQUEST_COLS if c in row]
    placeholders = ", ".join(f":{c}" for c in cols)
    with engine.begin() as conn:
        conn.execute(
            text(f"INSERT INTO requests ({', '.join(cols)}) VALUES ({placeholders})"),
            {c: row.get(c) for c in cols},
        )


def update_request(row_id: int, row: dict):
    engine = get_engine()
    cols = [c for c in REQUEST_COLS if c in row]
    set_clause = ", ".join(f"{c} = :{c}" for c in cols)
    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE requests SET {set_clause}, updated_at = now() WHERE id = :id"),
            {**{c: row.get(c) for c in cols}, "id": row_id},
        )


def delete_request(row_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM requests WHERE id = :id"), {"id": row_id})
