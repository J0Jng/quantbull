import os
from sqlmodel import SQLModel, create_engine

# Use DATABASE_URL env var; default to sqlite for quick local runs.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dev_quantbull.db",
)

# For Postgres, set e.g. postgresql+psycopg2://user:pass@localhost:5432/quantbull
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
