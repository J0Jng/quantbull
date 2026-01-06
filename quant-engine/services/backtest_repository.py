import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import select

from db import get_session
from models.backtest_record import BacktestRecord, BacktestStatus
from schemas.backtest import BacktestRequest


class BacktestRepository:
    @staticmethod
    def create_stub(request: BacktestRequest, backtest_id: Optional[str] = None, task_id: Optional[str] = None) -> BacktestRecord:
        record_id = backtest_id or f"backtest_{uuid.uuid4().hex[:8]}"
        
        # 多标的回测：用逗号连接 symbols 或使用 "MULTI"
        stock_code = request.stock_code
        if not stock_code and request.symbols:
            stock_code = ",".join(request.symbols[:5])  # 最多显示前5个
            if len(request.symbols) > 5:
                stock_code += f",... (共{len(request.symbols)}只)"
        elif not stock_code:
            stock_code = "PORTFOLIO"  # 股票池模式
        
        record = BacktestRecord(
            id=record_id,
            task_id=task_id,
            stock_code=stock_code,
            start_date=request.start_date,
            end_date=request.end_date,
            data_source=request.data_source,
            strategy_code=request.strategy_code,
            params=request.model_dump(),
            status=BacktestStatus.pending,
        )
        with get_session() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    @staticmethod
    def mark_running(backtest_id: str) -> None:
        BacktestRepository._update(backtest_id, status=BacktestStatus.running)

    @staticmethod
    def mark_success(backtest_id: str, metrics: Dict[str, Any], equity_curve: List[Dict[str, Any]], message: Optional[str] = None) -> None:
        BacktestRepository._update(
            backtest_id,
            status=BacktestStatus.success,
            metrics=metrics,
            equity_curve=equity_curve,
            message=message,
        )

    @staticmethod
    def mark_failed(backtest_id: str, error_message: str, error_code: str = "exception") -> None:
        BacktestRepository._update(backtest_id, status=BacktestStatus.failed, message=error_message, error_code=error_code)

    @staticmethod
    def link_task(backtest_id: str, task_id: str) -> None:
        BacktestRepository._update(backtest_id, task_id=task_id)

    @staticmethod
    def get(backtest_id: str) -> Optional[BacktestRecord]:
        with get_session() as session:
            stmt = select(BacktestRecord).where(BacktestRecord.id == backtest_id)
            return session.exec(stmt).first()

    @staticmethod
    def list(limit: int = 10, offset: int = 0) -> List[BacktestRecord]:
        with get_session() as session:
            stmt = select(BacktestRecord).offset(offset).limit(limit)
            return list(session.exec(stmt).all())

    @staticmethod
    def _update(backtest_id: str, **fields) -> None:
        with get_session() as session:
            rec = session.get(BacktestRecord, backtest_id)
            if not rec:
                return
            for k, v in fields.items():
                setattr(rec, k, v)
            rec.updated_at = datetime.utcnow()
            session.add(rec)
            session.commit()
