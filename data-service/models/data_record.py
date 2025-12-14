from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DataRecord(BaseModel):
    id: str
    source: str
    content: str
    tags: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


