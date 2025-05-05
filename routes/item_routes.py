from flask import Blueprint, request, Response
import json
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from utils.db import db
from utils.auth import token_required

def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json",
        status=status
    )

item_routes = Blueprint('item_routes', __name__, url_prefix='/item')
@item_routes.route('/my', methods=['GET'])
@token_required
def get_item_list():
    """
    내가 보유한 아이템 목록 조회
      - optional: ?category=<카테고리> 로 필터링 (육지아이템, 바다아이템, 캐릭터아이템)
      - item_id, item_type(name), used 여부 반환
    """
    try:
        user_id = ObjectId(request.user_id)
        category = request.args.get("category")  # e.g. "육지아이템", "바다아이템", "캐릭터아이템"

        # Aggregation pipeline
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$lookup": {
                "from": "item_catalog",
                "localField": "item_type",
                "foreignField": "name",
                "as": "catalog"
            }},
            {"$unwind": "$catalog"},
        ]

        # category 파라미터가 넘어오면 catalog.category 로 필터링
        if category:
            pipeline.append({"$match": {"catalog.category": category}})

        # 최종 projection: 필요한 필드만
        pipeline.append({"$project": {
            "_id": 0,
            "item_id": {"$toString": "$_id"},
            "item_type": "$item_type",
            "used": "$used"
        }})

        items = list(db.user_item.aggregate(pipeline))
        return json_kor({"items": items})

    except Exception as e:
        return json_kor({"error": str(e)}, 500)



@item_routes.route('/<item_id>', methods=['GET'])
@token_required
def get_item_detail(item_id):
    """
    특정 아이템 상세 조회
      - item_type, name, description, used, granted_at 등
    """
    try:
        user_id = ObjectId(request.user_id)
        uid = ObjectId(item_id)

        # 1) 먼저 user_item에서 본인 소유 확인
        ui = db.user_item.find_one(
            {"_id": uid, "user_id": user_id}
        )
        if not ui:
            return json_kor({"error": "해당 아이템을 찾을 수 없거나 소유 권한이 없습니다."}, 404)

        # 2) item_catalog에서 description 가져오기
        catalog = db.item_catalog.find_one(
            {"name": ui["item_type"]},
            {"_id": 0, "description": 1}
        ) or {}

        detail = {
            "item_id": item_id,
            "item_type": ui["item_type"],
            "used": ui.get("used", False),
            "granted_at": ui.get("granted_at"),
            "description": catalog.get("description", "")
        }
        return json_kor({"item": detail})

    except Exception as e:
        return json_kor({"error": str(e)}, 500)


@item_routes.route('/use', methods=['POST'])
@token_required
def use_item():
    """
    아이템 사용 처리
      - body에 item_id를 넘겨, used=True/used_at 기록 후 상세 info 반환
    """
    try:
        data = request.get_json()
        item_id = data.get("item_id")
        if not item_id:
            return json_kor({"error": "item_id가 필요합니다."}, 400)

        user_id = ObjectId(request.user_id)
        uid = ObjectId(item_id)

        # 1) user_item 업데이트
        result = db.user_item.find_one_and_update(
            {"_id": uid, "user_id": user_id, "used": False},
            {"$set": {"used": True, "used_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER
        )
        if not result:
            return json_kor({"error": "사용할 수 있는 아이템이 없습니다."}, 400)

        # 2) catalog에서 description 조회
        catalog = db.item_catalog.find_one(
            {"name": result["item_type"]},
            {"_id": 0, "description": 1}
        ) or {}

        used_info = {
            "item_id": item_id,
            "item_type": result["item_type"],
            "description": catalog.get("description", ""),
            "used_at": result.get("used_at")
        }
        return json_kor({
            "message": "아이템이 성공적으로 사용되었습니다.",
            "used_item": used_info
        })

    except Exception as e:
        return json_kor({"error": str(e)}, 500)
