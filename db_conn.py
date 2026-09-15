"""
Database connection helper. Reads config from environment variables
(or a local .env file if you use python-dotenv, see .env.example).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def _database_url() -> str:
    # Either set DATABASE_URL directly, or these individual PG* vars.
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD", "postgres")
    host = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", "5432")
    db = os.environ.get("PGDATABASE", "programme_tracker")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(_database_url(), pool_pre_ping=True)
    return _engine
