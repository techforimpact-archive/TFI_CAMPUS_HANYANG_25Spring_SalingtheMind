from flask import Blueprint, request, Response
from flasgger import swag_from  # (선택)
import json
from datetime import datetime
from bson import ObjectId
import random
from pymongo import ReturnDocument 
from utils.db import db
from utils.auth import token_required
from utils.config import POINT_RULES

# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json",
        status=status
    )

reward_routes = Blueprint('reward_routes', __name__, url_prefix='/reward')

LEVEL_UP_THRESHOLD = 50

@reward_routes.route('/grant', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Reward'],
    'description': '포인트 적립 후, 레벨업시 새로운 아이템 무작위 지급',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Bearer 토큰'},
        {'name': 'body', 'in': 'body', 'required': True,
         'schema': {'type': 'object', 'properties': {'action': {'type': 'string', 'example': 'write_letter'}}, 'required': ['action']}}
    ],
    'responses': {
        200: {'description': '성공적으로 포인트 적립 및 아이템 지급',
              'schema': {'type': 'object','properties':{'message':{'type':'string'},'action':{'type':'string'},'new_items':{'type':'array','items':{'type':'object','properties':{'name':{'type':'string'},'description':{'type':'string'},'category':{'type':'string'}}}}}}},
        400: {'description': '잘못된 액션입니다.'},
        500: {'description': '서버 오류'}
    }
})
def grant_point():
    """
    포인트 적립 후, 새로운 아이템 무작위 지급
    """
    data = request.get_json()
    action = data.get("action")
    if action not in POINT_RULES:
        return json_kor({"error": "올바르지 않은 액션입니다."}, 400)

    user_id = ObjectId(request.user_id)
    point_gain = POINT_RULES[action]

    # 1) 유저 정보 조회 및 포인트 지급
    user = db.user.find_one({"_id": user_id}, {"point": 1, "level": 1})
    if not user:
        return json_kor({"error": "사용자를 찾을 수 없습니다."}, 404)

    current_point = user.get("point", 0)
    current_level = user.get("level", 1)
    new_point = current_point + point_gain
    leveled_up = False
    new_items = []

    # 2) 레벨업 시에만 아이템 1개 무작위 지급
    # 레벨업 여부 확인
    if new_point >= LEVEL_UP_THRESHOLD:
        current_level += 1
        new_point = 0
        leveled_up = True

        # 보유 중인 아이템 목록 조회
        owned_items = db.user_item.distinct("item_type", {"user_id": user_id})
        
        # 신규 후보 아이템 조회
        item_pool = list(db.item_catalog.find(
            {"name": {"$nin": owned_items}},
            {"_id": 0, "name": 1, "description": 1, "category": 1}
        ))

        # 아이템 지급
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

   # 포인트와 레벨 갱신
    db.user.update_one(
        {"_id": user_id},
        {"$set": {"point": new_point, "level": current_level}}
    )

    return json_kor({
        "message": f"{point_gain}포인트가 적립되었습니다.",
        "action": action,
        "leveled_up": leveled_up,
        "level": current_level,
        "new_items": new_items
    }, 200)

@reward_routes.route('/my', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Reward'],
    'description': '현재 유저의 포인트 및 레벨 조회',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Bearer 토큰'}
    ],
    'responses': {
        200: {'description': '포인트 및 레벨 조회 성공',
              'schema': {'type': 'object','properties':{'nickname':{'type':'string'},'point':{'type':'integer'},'level': {'type': 'integer'}}}},
        404: {'description': '사용자를 찾을 수 없음'},
        500: {'description': '서버 오류'}
    }
})
def get_my_point():
    """
    현재 유저가 보유한 포인트 및 레벨 조회
    """
    try:
        user_id = ObjectId(request.user_id)
        user = db.user.find_one({"_id": user_id}, {"_id":0, "nickname":1, "point":1, "level": 1})
        if not user:
            return json_kor({"error": "사용자를 찾을 수 없습니다."}, 404)
        return json_kor({"nickname": user.get("nickname", ""), "point": user.get("point", 0), "level": user.get("level", 1)})
    except Exception as e:
        return json_kor({"error": str(e)}, 500)
