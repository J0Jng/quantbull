from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session
from sqlalchemy.orm import sessionmaker

from db import engine


SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
