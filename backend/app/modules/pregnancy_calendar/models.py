# models.py — MongoDB document schema cho Pregnancy Milestones
from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId
from pydantic import BaseModel, Field
from enum import Enum


class PyObjectId(str):
    """Custom type để handle MongoDB ObjectId trong Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)


class CategoryEnum(str, Enum):
    """Categories cho mỗi milestone."""
    CHECKUP = "checkup"
    SHOPPING = "shopping"
    PREPARATION = "preparation"
    BOOKING = "booking"
    OTHER = "other"


class StatusEnum(str, Enum):
    """Trạng thái của milestone."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PriorityEnum(str, Enum):
    """Mức độ ưu tiên."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    """Subtask/checklist item trong milestone."""
    id: PyObjectId | None = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    is_done: bool = Field(default=False)
    due_date: datetime | None = Field(default=None)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class PregnancyMilestone(BaseModel):
    """Document shape trong MongoDB collection 'pregnancy_milestones'."""
    
    id: PyObjectId | None = Field(default=None, alias="_id")
    week: int = Field(..., ge=8, le=40)
    title: str = Field(..., min_length=1, max_length=100)
    category: CategoryEnum = Field(default=CategoryEnum.OTHER)
    due_date: datetime = Field(...)
    description: str = Field(default="", max_length=500)
    notes: str = Field(default="", max_length=2000)
    tasks: list[Task] = Field(default_factory=list)
    status: StatusEnum = Field(default=StatusEnum.PENDING)
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
