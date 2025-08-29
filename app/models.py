from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class SummaryType(str, Enum):
    BRIEF = "brief"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=10000)
    summary_type: SummaryType = Field(default=SummaryType.BRIEF)
    max_words: Optional[int] = Field(default=None, ge=10, le=500)
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    processing_time: float

class TaskSubmitRequest(BaseModel):
    text: str
    summary_type: SummaryType = SummaryType.BRIEF
    max_words: Optional[int] = None

class TaskResponse(BaseModel):
    task_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    message: str

class TaskResultResponse(BaseModel):
    task_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    result: Optional[SummarizeResponse] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
