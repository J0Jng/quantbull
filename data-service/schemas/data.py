from pydantic import BaseModel, Field, field_validator


class CleanRequest(BaseModel):
    source: str = Field(..., description="Data source identifier")
    content: str = Field(..., description="Raw text content")
    tags: list[str] = Field(default_factory=list, description="Optional tags")
                            #如果没有提供此字段，默认创建一个空列表 []
    @field_validator("source", "content")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value


class CleanResponse(CleanRequest):
    summary: str = Field(..., description="Human readable summary")


