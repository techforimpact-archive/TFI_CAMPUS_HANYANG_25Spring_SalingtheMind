from flask import Blueprint, request, Response
from flasgger import swag_from
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

@item_routes.route('/catalog', methods=['GET'])
@swag_from({
    'tags': ['Item'],
    'summary': '전체 아이템 카탈로그 조회 (비인증)',
    'responses': {
        200: {
            'description': '아이템 카탈로그 리스트 반환'
        },
        500: {
            'description': '서버 에러'
        }
    }
})
def get_item_catalog():
    try:
        catalog = list(db.item_catalog.find({}, {"_id": 0}))
        return json_kor({"catalog": catalog})
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@item_routes.route('/my', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Item'],
    'summary': '내가 보유한 아이템 목록 조회',
    'parameters': [
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': '필터링할 카테고리 (예: 바다아이템, 육지아이템, 캐릭터아이템)'
        }
    ],
    'responses': {
        200: {
            'description': '보유 아이템 목록 조회 성공'
        },
        500: {
            'description': '서버 내부 오류'
        }
    }
})
def get_item_list():
    try:
        user_id = ObjectId(request.user_id)
        category = request.args.get("category")
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
        if category:
            pipeline.append({"$match": {"catalog.category": category}})
        pipeline.append({"$project": {
            "_id": 0,
            "item_id": {"$toString": "$_id"},
            "name": "$item_type",
            "used": "$used",
            "category": "$catalog.category"
        }})
        items = list(db.user_item.aggregate(pipeline))
        return json_kor({"items": items})
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@item_routes.route('/<item_id>', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Item'],
    'summary': '특정 아이템 상세 조회',
    'parameters': [
        {
            'name': 'item_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '조회할 아이템 ID'
        }
    ],
    'responses': {
        200: {
            'description': '성공'
        },
        404: {
            'description': '소유권 없음 또는 존재하지 않음'
        },
        500: {
            'description': '서버 에러'
        }
    }
})
def get_item_detail(item_id):
    try:
        user_id = ObjectId(request.user_id)
        uid = ObjectId(item_id)
        ui = db.user_item.find_one({"_id": uid, "user_id": user_id})
        if not ui:
            return json_kor({"error": "해당 아이템을 찾을 수 없거나 소유 권한이 없습니다."}, 404)
        catalog = db.item_catalog.find_one(
            {"name": ui["item_type"]},
            {"_id": 0, "description": 1}
        ) or {}
        detail = {
            "item_id": item_id,
            "item_name": ui["item_type"],
            "used": ui.get("used", False),
            "granted_at": ui.get("granted_at"),
            "description": catalog.get("description", "")
        }
        return json_kor({"item": detail})
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@item_routes.route('/use', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Item'],
    'summary': '아이템 사용 처리',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'item_id': {
                            'type': 'string',
                            'description': '사용할 아이템 ID'
                        }
                    },
                    'required': ['item_id']
                }
            }
        }
    },
    'responses': {
        200: {'description': '사용 성공'},
        400: {'description': '잘못된 요청 또는 이미 사용된 아이템'},
        500: {'description': '서버 에러'}
    }
})
def use_item():
    try:
        data = request.get_json()
        item_id = data.get("item_id")
        if not item_id:
            return json_kor({"error": "item_id가 필요합니다."}, 400)
        user_id = ObjectId(request.user_id)
        uid = ObjectId(item_id)
        result = db.user_item.find_one_and_update(
            {"_id": uid, "user_id": user_id, "used": False},
            {"$set": {"used": True, "used_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER
        )
        if not result:
            return json_kor({"error": "사용할 수 있는 아이템이 없습니다."}, 400)
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

@item_routes.route('/unuse', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Item'],
    'summary': '아이템 사용 해제',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'item_id': {
                            'type': 'string',
                            'description': '해제할 아이템 ID'
                        }
                    },
                    'required': ['item_id']
                }
            }
        }
    },
    'responses': {
        200: {'description': '해제 성공'},
        400: {'description': '잘못된 요청 또는 이미 해제된 아이템'},
        500: {'description': '서버 에러'}
    }
})
def unuse_item():
    try:
        data = request.get_json()
        item_id = data.get("item_id")
        if not item_id:
            return json_kor({"error": "item_id가 필요합니다."}, 400)

        user_id = ObjectId(request.user_id)
        uid = ObjectId(item_id)

        result = db.user_item.find_one_and_update(
            {"_id": uid, "user_id": user_id, "used": True},
            {"$set": {"used": False, "used_at": None}},
            return_document=ReturnDocument.AFTER
        )

        if not result:
            return json_kor({"error": "이미 해제되었거나 존재하지 않는 아이템입니다."}, 400)

        catalog = db.item_catalog.find_one(
            {"name": result["item_type"]},
            {"_id": 0, "description": 1}
        ) or {}

        unused_info = {
            "item_id": item_id,
            "item_type": result["item_type"],
            "description": catalog.get("description", ""),
            "unused_at": datetime.utcnow()
        }

        return json_kor({
            "message": "아이템이 성공적으로 해제되었습니다.",
            "unused_item": unused_info
        })
    except Exception as e:
        return json_kor({"error": str(e)}, 500)
