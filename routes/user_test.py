import datetime
from flask import request, Blueprint, Response, make_response
from flasgger import swag_from
import jwt
from bson.objectid import ObjectId
from functools import wraps
import json
from utils.db import db
from utils.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

user_test = Blueprint('user', __name__, url_prefix='/api/users')

# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8",
        status=status
    )

def create_token(user_doc):
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "user_id": str(user_doc["_id"]),
        "nickname": user_doc["nickname"],
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

@user_test.route('/signup', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': '회원가입',
    'description': '사용자를 등록합니다. 닉네임, 나이, 성별은 필수이며, 주소/전화번호는 선택 항목입니다.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'nickname': {'type': 'string'},
                        'age': {'type': 'integer'},
                        'gender': {'type': 'string'},
                        'address': {'type': 'string'},
                        'phone': {'type': 'string'}
                    },
                    'required': ['nickname', 'age', 'gender']
                }
            }
        }
    },
    'responses': {
        201: {'description': '회원가입 성공'},
        400: {'description': '중복 닉네임 또는 필수 항목 누락'},
        500: {'description': '서버 에러'}
    }
})
def signup():
    try:
        data = request.get_json(force=True)
        
        nickname = data.get('nickname')
        age      = data.get('age')
        gender   = data.get('gender')
        address  = data.get('address')
        phone    = data.get('phone')

        if not nickname or age is None or not gender:
            return json_kor({"error": "닉네임, 나이, 성별은 필수입니다."}, 400)

        if db.user.find_one({"nickname": nickname}):
            return json_kor({"error": "이미 존재하는 닉네임입니다."}, 400)

        limited_access = not (address and phone)
        new_user = {
            "nickname": nickname,
            "age": age,
            "gender": gender,
            "address": address or "",
            "phone": phone or "",
            "point": 0,
            "level": 1,
            "limited_access": limited_access
        }

        result = db.user.insert_one(new_user)
        user_doc = db.user.find_one({"_id": result.inserted_id})
        token = create_token(user_doc)

        return json_kor({
            "message": "회원가입 성공!",
            "nickname": user_doc["nickname"],
            "limited_access": limited_access,
            "token": token
        }, 201)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@user_test.route('/login', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': '로그인',
    'description': '닉네임을 입력하면 토큰이 반환됩니다.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'nickname': {'type': 'string'}
                    },
                    'required': ['nickname']
                }
            }
        }
    },
    'responses': {
        200: {'description': '로그인 성공'},
        400: {'description': '닉네임 누락'},
        404: {'description': '사용자 없음'},
        500: {'description': '서버 에러'}
    }
})
def login():
    try:
        data = request.get_json()
        nickname = data.get('nickname')

        if not nickname:
            return json_kor({"error": "닉네임을 입력해주세요."}, 400)

        user_doc = db.user.find_one({"nickname": nickname})
        
        if not user_doc:
            return json_kor({"error": "해당 닉네임의 사용자가 존재하지 않습니다."}, 404)

        token = create_token(user_doc)
        user_id = user_doc['_id']
        
        #####더미용 데이터#####
        letter = {"_id": ObjectId(), "from": ObjectId('68260f67f02ef2dccfdeffca'), "to": user_id, "title": '익명의 사용자에게서 온 편지',"emotion": '슬픔', "content": '정말 친하다고 생각했던 친구와 크게 싸웠어요. 좋은 친구라고 생각했는데 아니였던 것 같아요 우정이 영원할 수는 없는 걸까요?', "status": 'sent',
              "saved": False, "created_at": datetime.datetime.now()}
        #######여기까지는 실제 배포시에는 삭제!!!!!
        db.letter.insert_one(letter)
        return json_kor({
            "message": "로그인 성공!",
            "nickname": user_doc["nickname"],
            "limited_access": user_doc.get("limited_access", False),
            "token": token
        })
        
    except Exception as e:
        return json_kor({"error": str(e)}, 500)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return json_kor({"error": "Authorization 헤더가 필요합니다."}, 401)
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload["user_id"]
            user = db.user.find_one({"_id": ObjectId(user_id)})
            if not user:
                return json_kor({"error": "사용자를 찾을 수 없습니다."}, 404)
            request.user = user
            request.user_id = str(user["_id"])
        except jwt.ExpiredSignatureError:
            return json_kor({"error": "토큰이 만료되었습니다."}, 401)
        except jwt.InvalidTokenError:
            return json_kor({"error": "유효하지 않은 토큰입니다."}, 401)
        return f(*args, **kwargs)
    return decorated

@user_test.route('/update', methods=['PATCH'])
@token_required
@swag_from({
    'tags': ['User'],
    'summary': '회원 정보 수정',
    'description': '회원의 닉네임, 나이, 성별, 주소, 전화번호를 수정합니다.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer 액세스 토큰'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'nickname': {'type': 'string'},
                        'age': {'type': 'integer'},
                        'gender': {'type': 'string'},
                        'address': {'type': 'string'},
                        'phone': {'type': 'string'}
                    }
                }
            }
        }
    },
    'responses': {
        200: {'description': '수정 성공'},
        400: {'description': '중복 닉네임'},
        401: {'description': '인증 실패'},
        500: {'description': '서버 에러'}
    }
})
def update_user():
    try:
        user_id = request.user["_id"]
        data = request.get_json()

        # 나이와 성별은 수정에서 제외
        update_fields = {k: v for k, v in data.items() if k in ['nickname', 'address', 'phone']}
        # 아무 필드도 제공되지 않았을 경우 예외 처리
        if not update_fields:
            return json_kor({"error": "수정할 항목이 제공되지 않았습니다."}, 400)
        
        if "nickname" in update_fields:
            if db.user.find_one({"nickname": update_fields["nickname"], "_id": {"$ne": user_id}}):
                return json_kor({"error": "이미 존재하는 닉네임입니다."}, 400)

        if update_fields:
            db.user.update_one({"_id": user_id}, {"$set": update_fields})

        updated_user = db.user.find_one({"_id": user_id})
        updated_user["_id"] = str(updated_user["_id"])
        return json_kor({
            "message": "회원 정보가 성공적으로 수정되었습니다.",
            "updated_user": updated_user
        })
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@user_test.route('/me', methods=['GET'])
@token_required
@swag_from({
    'tags': ['User'],
    'summary': '내 정보 조회',
    'description': '로그인한 사용자의 정보를 반환합니다.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer 액세스 토큰'
        }
    ],
    'responses': {
        200: {
            'description': '사용자 정보 반환',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'user': {
                                'type': 'object',
                                'properties': {
                                    'nickname': {'type': 'string'},
                                    'age': {'type': 'integer'},
                                    'gender': {'type': 'string'},
                                    'address': {'type': 'string'},
                                    'phone': {'type': 'string'},
                                    'point': {'type': 'integer'},
                                    'level': {'type': 'integer'},
                                    'limited_access': {'type': 'boolean'}
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {'description': '인증 실패'},
        404: {'description': '사용자 없음'}
    }
})
def get_my_info():
    try:
        user = request.user
        user_info = {
            "nickname": user.get("nickname"),
            "age": user.get("age"),
            "gender": user.get("gender"),
            "address": user.get("address", ""),
            "phone": user.get("phone", ""),
            "point": user.get("point", 0),
            "level": user.get("level", 1),
            "limited_access": user.get("limited_access", True)
        }
        return json_kor({"user": user_info}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)
