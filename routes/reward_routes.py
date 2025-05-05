from flask import Blueprint, request, Response
import json, random
from datetime import datetime
from bson import ObjectId
from utils.db import db
from utils.auth import token_required
from utils.config import POINT_RULES, ITEM_THRESHOLDS

reward_routes = Blueprint('reward_routes', __name__, url_prefix='/reward')

# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8",
        status=status
    )

@reward_routes.route('/grant', methods=['POST'])
@token_required
def grant_point():
    """
    포인트 적립 및 임계치 달성 시 아이템 지급
    ---
    tags:
      - Reward
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            action:
              type: string
              description: 수행한 액션 키
          required:
            - action
    responses:
      200:
        description: 포인트 적립 및 신규 아이템 지급 결과
        schema:
          type: object
          properties:
            message:
              type: string
            action:
              type: string
            new_items:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  description:
                    type: string
      400:
        description: 잘못된 액션 또는 요청 오류
      500:
        description: 서버 에러
    """
    try:
        data = request.get_json() or {}
        action = data.get("action")
        if action not in POINT_RULES:
            return json_kor({"error": "올바르지 않은 액션입니다."}, 400)

        user_id = ObjectId(request.user_id)
        point = POINT_RULES[action]

        # 포인트 적립
        user = db.user.find_one_and_update(
            {"_id": user_id},
            {"$inc": {"point": point}},
            return_document=True
        )
        current_pt = user.get("point", 0)
        awarded = set(user.get("awarded_thresholds", []))
        new_items = []

        # 임계치 달성 시 아이템 지급
        for threshold in ITEM_THRESHOLDS:
            if current_pt >= threshold and threshold not in awarded:
                owned = db.user_item.distinct("item_type", {"user_id": user_id})
                pool = list(db.item_catalog.find({"name": {"$nin": owned}}))
                if not pool:
                    continue
                item = random.choice(pool)
                doc = {
                    "user_id": user_id,
                    "item_type": item["name"],
                    "used": False,
                    "granted_at": datetime.utcnow()
                }
                db.user_item.insert_one(doc)
                db.user.update_one(
                    {"_id": user_id},
                    {"$push": {"awarded_thresholds": threshold}}
                )
                new_items.append({
                    "name": item["name"],
                    "description": item.get("description", "")
                })

        return json_kor({
            "message": f"{point}포인트가 적립되었습니다.",
            "action": action,
            "new_items": new_items
        }, 200)

    except Exception as e:
        return json_kor({"error": str(e)}, 500)
