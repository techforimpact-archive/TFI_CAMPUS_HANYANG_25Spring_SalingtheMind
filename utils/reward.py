# utils/reward.py

import random
from datetime import datetime
from bson import ObjectId
from utils.db import db
from utils.config import POINT_RULES

LEVEL_UP_THRESHOLD = 100

def grant_point_by_action(user_id, action, extra_data=None):
    if action not in POINT_RULES:
        return False, f"올바르지 않은 액션입니다: {action}"

    base_point = POINT_RULES[action]
    bonus_point = 0

    # 글자 수 기준 보너스 점수 부여 (예: 200자 이상)
    if action == "write_letter" and extra_data:
        content = extra_data.get("content", "")
        if len(content) >= 200:
            bonus_point = 5

    total_point = base_point + bonus_point

    user = db.user.find_one({"_id": user_id}, {"point": 1, "level": 1})
    if not user:
        return False, "사용자를 찾을 수 없습니다."

    current_point = user.get("point", 0)
    current_level = user.get("level", 1)
    new_point = current_point + total_point
    leveled_up = False
    new_items = []

    # 레벨업 조건 충족 시 처리
    if new_point >= LEVEL_UP_THRESHOLD:
        current_level += 1
        new_point = 0
        leveled_up = True

        owned_items = db.user_item.distinct("item_type", {"user_id": user_id})
        item_pool = list(db.item_catalog.find(
            {"name": {"$nin": owned_items}},
            {"_id": 0, "name": 1, "description": 1, "category": 1}
        ))

        if item_pool:
            reward_item = random.choice(item_pool)
            db.user_item.insert_one({
                "user_id": user_id,
                "item_type": reward_item["name"],
                "used": False,
                "granted_at": datetime.utcnow()
            })
            new_items.append({
                "name": reward_item["name"],
                "description": reward_item.get("description", ""),
                "category": reward_item.get("category", "")
            })

    db.user.update_one(
        {"_id": user_id},
        {"$set": {"point": new_point, "level": current_level}}
    )

    return True, {
        "point": total_point,
        "base_point": base_point,
        "bonus_point": bonus_point,
        "leveled_up": leveled_up,
        "level": current_level,
        "new_items": new_items
    }
