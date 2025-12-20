from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import select

from models import User, UserCreate, UserRead, Strategy, StrategyCreate, StrategyRead, DailyReport, News, Quote
from session import get_session
from db import create_db_and_tables

app = FastAPI(title="QuantBull ORM Example")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_db():
    with get_session() as session:
        yield session


@app.post("/users/", response_model=UserRead)
def create_user(payload: UserCreate, session=Depends(get_db)):
    user = User(username=payload.username, email=payload.email, full_name=payload.full_name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session=Depends(get_db)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/strategies/", response_model=StrategyRead)
def create_strategy(payload: StrategyCreate, session=Depends(get_db)):
    strategy = Strategy(**payload.dict())
    session.add(strategy)
    session.commit()
    session.refresh(strategy)
    return strategy


@app.get("/strategies/", response_model=List[StrategyRead])
def list_strategies(session=Depends(get_db)):
    stmt = select(Strategy).order_by(Strategy.score.desc())
    return session.exec(stmt).all()


@app.post("/daily_reports/", response_model=dict)
def create_report(report: DailyReport, session=Depends(get_db)):
    session.add(report)
    session.commit()
    session.refresh(report)
    return {"id": report.id}


@app.post("/quotes/", response_model=dict)
def ingest_quote(q: Quote, session=Depends(get_db)):
    session.add(q)
    session.commit()
    session.refresh(q)
    return {"id": q.id}
