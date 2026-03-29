# schemas.py — Pydantic schemas cho API requests/responses
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class CategoryEnum(str, Enum):
    CHECKUP = "checkup"
    SHOPPING = "shopping"
    PREPARATION = "preparation"
    BOOKING = "booking"
    OTHER = "other"


class StatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskSchema(BaseModel):
    """Subtask schema."""
    id: str | None = None
    name: str = Field(..., min_length=1, max_length=200)
    is_done: bool = False
    due_date: datetime | None = None


class CreateMilestoneSchema(BaseModel):
    """Request schema để tạo milestone mới."""
    week: int = Field(..., ge=8, le=40)
    title: str = Field(..., min_length=1, max_length=100)
    category: CategoryEnum = CategoryEnum.OTHER
    due_date: datetime
    description: str = Field(default="", max_length=500)
    notes: str = Field(default="", max_length=2000)
    priority: PriorityEnum = PriorityEnum.MEDIUM


class UpdateMilestoneSchema(BaseModel):
    """Request schema để update milestone."""
    title: str | None = None
    category: CategoryEnum | None = None
    due_date: datetime | None = None
    description: str | None = None
    notes: str | None = None
    tasks: list[TaskSchema] | None = None
    status: StatusEnum | None = None
    priority: PriorityEnum | None = None


class MilestoneResponseSchema(BaseModel):
    """Response schema cho milestone."""
    id: str
    week: int
    title: str
    category: CategoryEnum
    due_date: datetime
    description: str
    notes: str
    tasks: list[TaskSchema]
    status: StatusEnum
    priority: PriorityEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MilestoneListResponseSchema(BaseModel):
    """Response schema cho danh sách milestones."""
    total: int
    milestones: list[MilestoneResponseSchema]
