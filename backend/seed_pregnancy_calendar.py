# seed_pregnancy_calendar.py — Seed default pregnancy milestones
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from app.core.config import settings

DEFAULT_MILESTONES = [
    {"week": 8, "title": "Khám thai lần đầu tiên", "category": "checkup", "description": "Khám thai đầu tiên", "notes": "Mang theo chứng chỉ khai sinh", "priority": "high", "days": 0},
    {"week": 12, "title": "Siêu âm lần 1 + xét nghiệm máu", "category": "checkup", "description": "Siêu âm 3D check dị tật", "notes": "Có thể biết giới tính bé", "priority": "high", "days": 28},
    {"week": 16, "title": "Khám thai định kỳ", "category": "checkup", "description": "Khám sức khỏe định kỳ", "notes": "Check huyết áp, cân nặng", "priority": "medium", "days": 56},
    {"week": 16, "title": "Bắt đầu mua sắm đồ cho bé", "category": "shopping", "description": "Mua nôi, quần áo, bình sữa", "notes": "Chuẩn bị đồ dùng", "priority": "medium", "days": 56},
    {"week": 20, "title": "Siêu âm lần 2 (giữa thai kỳ)", "category": "checkup", "description": "Siêu âm chi tiết", "notes": "Check phát triển chi tiết", "priority": "high", "days": 84},
    {"week": 24, "title": "Kiểm tra đường huyết", "category": "checkup", "description": "Test glucose tolerance", "notes": "Uống nước đường", "priority": "high", "days": 112},
    {"week": 28, "title": "Chuẩn bị cho phòng sinh", "category": "preparation", "description": "Tìm hiểu về phòng sinh", "notes": "Tập thở, vận động nhẹ", "priority": "medium", "days": 140},
    {"week": 28, "title": "Hoàn thành chuẩn bị đồ dùng thiết yếu", "category": "shopping", "description": "Mua đầy đủ đồ dùng cho mẹ", "notes": "Áo ngủ, băng vệ sinh siêu thấm", "priority": "medium", "days": 140},
    {"week": 30, "title": "Khám thai + check vị trí thai", "category": "checkup", "description": "Check vị trí thai", "notes": "Bé có ngửa đầu xuống", "priority": "high", "days": 154},
    {"week": 32, "title": "Tham gia lớp chuẩn bị sinh con", "category": "preparation", "description": "Học về quá trình sinh nở", "notes": "Tham gia với chồng/gia đình", "priority": "medium", "days": 168},
    {"week": 32, "title": "Đặt lịch phòng sinh", "category": "booking", "description": "Chọn bệnh viện và đặt lịch", "notes": "Xác nhận với bác sĩ", "priority": "high", "days": 168},
    {"week": 34, "title": "Siêu âm lần 3 (cuối thai kỳ)", "category": "checkup", "description": "Siêu âm cuối cùng", "notes": "Kiểm tra phát triển bé", "priority": "high", "days": 182},
    {"week": 34, "title": "Chuẩn bị hành trang đi bệnh viện", "category": "preparation", "description": "Chuẩn bị ba lô", "notes": "Quần áo cho mẹ, cho bé", "priority": "medium", "days": 182},
    {"week": 36, "title": "Khám thai định kỳ (40% mẹ sinh tuần này)", "category": "checkup", "description": "Khám sức khỏe, kiểm tra lần cuối", "notes": "Hỏi dấu hiệu sắp sinh", "priority": "high", "days": 196},
    {"week": 40, "title": "Dự kiến ngày sinh con", "category": "preparation", "description": "Tuần dự kiến sinh", "notes": "Chuẩn bị tinh thần", "priority": "high", "days": 224},
]

def seed_milestones():
    """Seed default milestones."""
    try:
        client = MongoClient(settings.mongodb_url)
        db = client[settings.db_name]
        collection = db["pregnancy_milestones"]
        
        if collection.count_documents({}) > 0:
            print("Database already seeded.")
            return
        
        start_date = datetime.now(timezone.utc)
        documents = []
        
        for milestone in DEFAULT_MILESTONES:
            due_date = start_date + timedelta(days=milestone["days"])
            doc = {
                "week": milestone["week"],
                "title": milestone["title"],
                "category": milestone["category"],
                "due_date": due_date,
                "description": milestone["description"],
                "notes": milestone["notes"],
                "tasks": [],
                "status": "pending",
                "priority": milestone["priority"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            documents.append(doc)
        
        result = collection.insert_many(documents)
        print(f"✅ Seeded {len(result.inserted_ids)} milestones!")
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    seed_milestones()
