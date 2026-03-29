# services.py — Business logic cho Pregnancy Milestones
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_db
from app.modules.pregnancy_calendar.models import PregnancyMilestone, Task, StatusEnum, CategoryEnum
from app.modules.pregnancy_calendar.schemas import (
    CreateMilestoneSchema,
    UpdateMilestoneSchema,
    MilestoneResponseSchema,
    TaskSchema,
)


class PregnancyMilestoneService:
    """Service class để quản lý Pregnancy Milestones."""
    
    COLLECTION_NAME = "pregnancy_milestones"
    
    @staticmethod
    def get_collection():
        """Lấy MongoDB collection."""
        db = get_db()
        return db[PregnancyMilestoneService.COLLECTION_NAME]
    
    @staticmethod
    def create_milestone(create_data: CreateMilestoneSchema) -> MilestoneResponseSchema:
        """Tạo milestone mới."""
        collection = PregnancyMilestoneService.get_collection()
        
        milestone_doc = {
            "week": create_data.week,
            "title": create_data.title,
            "category": create_data.category.value,
            "due_date": create_data.due_date,
            "description": create_data.description,
            "notes": create_data.notes,
            "tasks": [],
            "status": "pending",
            "priority": create_data.priority.value,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        result = collection.insert_one(milestone_doc)
        milestone_doc["_id"] = result.inserted_id
        
        return PregnancyMilestoneService._doc_to_response(milestone_doc)
    
    @staticmethod
    def get_milestone(milestone_id: str) -> MilestoneResponseSchema | None:
        """Lấy 1 milestone theo ID."""
        collection = PregnancyMilestoneService.get_collection()
        
        try:
            doc = collection.find_one({"_id": ObjectId(milestone_id)})
            if doc:
                return PregnancyMilestoneService._doc_to_response(doc)
        except:
            pass
        
        return None
    
    @staticmethod
    def get_all_milestones(
        week: int | None = None,
        status: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[MilestoneResponseSchema], int]:
        """Lấy danh sách milestones với optional filter."""
        collection = PregnancyMilestoneService.get_collection()
        
        filter_query = {}
        if week is not None:
            filter_query["week"] = week
        if status is not None:
            filter_query["status"] = status
        if category is not None:
            filter_query["category"] = category
        
        total = collection.count_documents(filter_query)
        
        docs = list(
            collection.find(filter_query)
            .sort("week", 1)
            .skip(skip)
            .limit(limit)
        )
        
        milestones = [
            PregnancyMilestoneService._doc_to_response(doc) for doc in docs
        ]
        
        return milestones, total
    
    @staticmethod
    def update_milestone(
        milestone_id: str,
        update_data: UpdateMilestoneSchema,
    ) -> MilestoneResponseSchema | None:
        """Update milestone."""
        collection = PregnancyMilestoneService.get_collection()
        
        try:
            update_dict = {}
            
            if update_data.title is not None:
                update_dict["title"] = update_data.title
            if update_data.category is not None:
                update_dict["category"] = update_data.category.value
            if update_data.due_date is not None:
                update_dict["due_date"] = update_data.due_date
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.notes is not None:
                update_dict["notes"] = update_data.notes
            if update_data.tasks is not None:
                update_dict["tasks"] = [
                    {
                        "_id": ObjectId(t.id) if t.id else ObjectId(),
                        "name": t.name,
                        "is_done": t.is_done,
                        "due_date": t.due_date,
                    }
                    for t in update_data.tasks
                ]
            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            if update_data.priority is not None:
                update_dict["priority"] = update_data.priority.value
            
            update_dict["updated_at"] = datetime.now(timezone.utc)
            
            result = collection.find_one_and_update(
                {"_id": ObjectId(milestone_id)},
                {"$set": update_dict},
                return_document=True,
            )
            
            if result:
                return PregnancyMilestoneService._doc_to_response(result)
        except:
            pass
        
        return None
    
    @staticmethod
    def delete_milestone(milestone_id: str) -> bool:
        """Xoá milestone."""
        collection = PregnancyMilestoneService.get_collection()
        
        try:
            result = collection.delete_one({"_id": ObjectId(milestone_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def add_task_to_milestone(
        milestone_id: str,
        task: TaskSchema,
    ) -> MilestoneResponseSchema | None:
        """Thêm task vào milestone."""
        collection = PregnancyMilestoneService.get_collection()
        
        try:
            task_doc = {
                "_id": ObjectId(task.id) if task.id else ObjectId(),
                "name": task.name,
                "is_done": task.is_done,
                "due_date": task.due_date,
            }
            
            result = collection.find_one_and_update(
                {"_id": ObjectId(milestone_id)},
                {
                    "$push": {"tasks": task_doc},
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                },
                return_document=True,
            )
            
            if result:
                return PregnancyMilestoneService._doc_to_response(result)
        except:
            pass
        
        return None
    
    @staticmethod
    def get_milestones_by_week_range(
        start_week: int,
        end_week: int,
    ) -> list[MilestoneResponseSchema]:
        """Lấy milestones trong khoảng tuần."""
        collection = PregnancyMilestoneService.get_collection()
        
        docs = list(
            collection.find({"week": {"$gte": start_week, "$lte": end_week}})
            .sort("week", 1)
        )
        
        return [
            PregnancyMilestoneService._doc_to_response(doc) for doc in docs
        ]
    
    @staticmethod
    def _doc_to_response(doc: dict) -> MilestoneResponseSchema:
        """Convert MongoDB document to response schema."""
        return MilestoneResponseSchema(
            id=str(doc["_id"]),
            week=doc["week"],
            title=doc["title"],
            category=doc["category"],
            due_date=doc["due_date"],
            description=doc.get("description", ""),
            notes=doc.get("notes", ""),
            tasks=[
                TaskSchema(
                    id=str(t.get("_id", "")),
                    name=t["name"],
                    is_done=t.get("is_done", False),
                    due_date=t.get("due_date"),
                )
                for t in doc.get("tasks", [])
            ],
            status=doc["status"],
            priority=doc["priority"],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at", doc["created_at"]),
        )
