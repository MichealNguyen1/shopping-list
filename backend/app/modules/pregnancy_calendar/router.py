# router.py — FastAPI router cho Pregnancy Calendar API
from fastapi import APIRouter, HTTPException, Query
from app.modules.pregnancy_calendar.services import PregnancyMilestoneService
from app.modules.pregnancy_calendar.schemas import (
    CreateMilestoneSchema,
    UpdateMilestoneSchema,
    MilestoneResponseSchema,
    MilestoneListResponseSchema,
    TaskSchema,
)

router = APIRouter(prefix="/milestones", tags=["pregnancy_calendar"])


@router.post("", response_model=MilestoneResponseSchema)
async def create_milestone(data: CreateMilestoneSchema):
    """Tạo milestone mới."""
    try:
        return PregnancyMilestoneService.create_milestone(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{milestone_id}", response_model=MilestoneResponseSchema)
async def get_milestone(milestone_id: str):
    """Lấy 1 milestone theo ID."""
    milestone = PregnancyMilestoneService.get_milestone(milestone_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


@router.get("", response_model=MilestoneListResponseSchema)
async def list_milestones(
    week: int | None = Query(None, ge=8, le=40),
    status: str | None = Query(None),
    category: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Lấy danh sách milestones."""
    milestones, total = PregnancyMilestoneService.get_all_milestones(
        week=week,
        status=status,
        category=category,
        skip=skip,
        limit=limit,
    )
    return MilestoneListResponseSchema(total=total, milestones=milestones)


@router.put("/{milestone_id}", response_model=MilestoneResponseSchema)
async def update_milestone(milestone_id: str, data: UpdateMilestoneSchema):
    """Update milestone."""
    milestone = PregnancyMilestoneService.update_milestone(milestone_id, data)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


@router.delete("/{milestone_id}")
async def delete_milestone(milestone_id: str):
    """Xoá milestone."""
    success = PregnancyMilestoneService.delete_milestone(milestone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return {"deleted": True}


@router.post("/{milestone_id}/tasks", response_model=MilestoneResponseSchema)
async def add_task(milestone_id: str, task: TaskSchema):
    """Thêm task vào milestone."""
    milestone = PregnancyMilestoneService.add_task_to_milestone(milestone_id, task)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


@router.get("/week/{start_week}/{end_week}", response_model=list[MilestoneResponseSchema])
async def get_milestones_by_week_range(start_week: int, end_week: int):
    """Lấy milestones trong khoảng tuần."""
    if start_week > end_week:
        raise HTTPException(status_code=400, detail="start_week must be <= end_week")
    if start_week < 8 or end_week > 40:
        raise HTTPException(status_code=400, detail="Week must be between 8 and 40")
    
    return PregnancyMilestoneService.get_milestones_by_week_range(start_week, end_week)
