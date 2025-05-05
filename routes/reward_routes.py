from flask import Blueprint, request, Response
import json
from datetime import datetime
from bson import ObjectId
from utils.db import db
from utils.auth import token_required
from utils.config import POINT_RULES, BOX_THRESHOLDS, REWARD_ITEMS
import random

# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json",
        status=status
    )

reward_routes = Blueprint('reward_routes', __name__, url_prefix='/reward')

@reward_routes.route('/grant', methods=['POST'])
@token_required
def grant_point():
    """
    포인트 적립 후 누적 임계치 도달 시 랜덤 박스 생성
    """
    data = request.get_json()
    action = data.get("action")
    if action not in POINT_RULES:
        return json_kor({"error": "올바르지 않은 액션입니다."}, 400)

    user_id = ObjectId(request.user_id)
    point = POINT_RULES[action]
    user = db.user.find_one_and_update(
        {"_id": user_id},
        {"$inc": {"point": point}},
        return_document=True
    )

    # 누적 포인트 기준 랜덤 박스 지급
    new_boxes = []
    current_pt = user.get("point", 0)
    awarded = set(user.get("awarded_thresholds", []))
    for threshold, box_type in BOX_THRESHOLDS.items():
        if current_pt >= threshold and threshold not in awarded:
            db.user_item.insert_one({
                "user_id": user_id,
                "item_type": box_type,
                "used": False,
                "granted_at": datetime.utcnow()
            })
            db.user.update_one(
                {"_id": user_id},
                {"$push": {"awarded_thresholds": threshold}}
            )
            new_boxes.append(box_type)

    return json_kor({
        "message": f"{point}포인트가 적립되었습니다.",
        "action": action,
        "boxes_created": new_boxes
    }, 200)

@reward_routes.route('/my', methods=['GET'])
@token_required
def get_my_point():
    """
    내 포인트 조회
    """
    try:
        user_id = ObjectId(request.user_id)
        user = db.user.find_one({"_id": user_id})
        if not user:
            return json_kor({"error": "사용자를 찾을 수 없습니다."}, 404)
        return json_kor({
            "nickname": user.get("nickname", ""),
            "point": user.get("point", 0)
        }, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@reward_routes.route('/open-box', methods=['POST'])
@token_required
def open_random_box():
    """
    랜덤 박스 개봉 후 실제 리워드 지급 (다수 아이템 가능)
    """
    try:
        user_id = ObjectId(request.user_id)
        box = db.user_item.find_one({
            "user_id": user_id,
            "item_type": {"$in": list(BOX_THRESHOLDS.values())},
            "used": False
        })
        if not box:
            return json_kor({"error": "사용 가능한 랜덤 박스가 없습니다."}, 400)

        box_type = box["item_type"]
        rule = REWARD_ITEMS.get(box_type, {"min_items": 1, "max_items": 1})
        count = random.randint(rule["min_items"], rule["max_items"])

        items = list(db.item_catalog.find({}))
        if not items:
            return json_kor({"error": "아이템 목록이 비어있습니다."}, 500)

        chosen = random.sample(items, min(count, len(items)))
        reward_names = [item["name"] for item in chosen]

        # 박스 사용 처리
        db.user_item.update_one(
            {"_id": box["_id"]},
            {"$set": {"used": True}}
        )

        now = datetime.utcnow()
        insert_docs = [{
            "user_id": user_id,
            "item_type": name,
            "used": False,
            "granted_at": now
        } for name in reward_names]
        db.user_item.insert_many(insert_docs)

        return json_kor({
            "message": f"{box_type}이(가) 개봉되었습니다!",
            "reward_items": reward_names
        }, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)
