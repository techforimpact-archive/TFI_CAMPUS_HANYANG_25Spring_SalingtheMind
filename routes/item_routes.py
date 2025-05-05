# item_routes.py
from flask import Blueprint, request, Response
import json
from bson import ObjectId
from utils.auth import token_required
from utils.db import db

# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json",
        status=status
    )

item_routes = Blueprint('item_routes', __name__, url_prefix='/item')

@item_routes.route('/catalog', methods=['GET'])
def get_item_catalog():
    """
    전체 아이템 목록 조회 (item_catalog 컬렉션 기준)
    """
    try:
        items = list(db.item_catalog.find({}, {"_id": 0}))
        return json_kor({"items": items}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@item_routes.route('/my', methods=['GET'])
@token_required
def get_my_items():
    """
    내가 보유한 미사용 아이템 조회 (user_item 컬렉션 기준)
    """
    try:
        user_id = ObjectId(request.user_id)
        items = list(db.user_item.find(
            {"user_id": user_id, "used": False},
            {"_id": 0, "item_type": 1, "granted_at": 1}
        ))
        return json_kor({"items": items}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@item_routes.route('/use', methods=['POST'])
@token_required
def use_item():
    """
    아이템 사용 처리 (user_item 컬렉션 기준)
    """
    try:
        data = request.get_json()
        item_type = data.get("item_type")
        user_id = ObjectId(request.user_id)

        result = db.user_item.find_one_and_update(
            {"user_id": user_id, "item_type": item_type, "used": False},
            {"$set": {"used": True}},
            return_document=True
        )
        if not result:
            return json_kor({"error": "사용할 수 있는 아이템이 없습니다."}, 400)
        return json_kor({"message": "아이템이 성공적으로 사용되었습니다."}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)
