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
def signup():
    try:
        data = request.get_json()
        nickname = data.get('nickname')
        age      = data.get('age')
        gender   = data.get('gender')
        address  = data.get('address')
        phone    = data.get('phone')

        if not nickname or age is None or not gender:
            return json_kor({"error": "닉네임, 나이, 성별은 필수입니다."}, 400)

        if db.user.find_one({"nickname": nickname}):
            return json_kor({"error": "이미 존재하는 닉네임입니다."}), 400

        limited_access = not (address and phone)
        new_user = {
            "nickname": nickname,
            "age": age,
            "gender": gender,
            "address": address or "",
            "phone": phone or "",
            "point": 0,
            "limited_access": limited_access
        }

        result = db.user.insert_one(new_user)
        user_doc = db.user.find_one({"_id": result.inserted_id})
        token = create_token(user_doc)

        resp = make_response(json_kor({
            "message": "회원가입 성공!",
            "nickname": user_doc["nickname"],
            "limited_access": limited_access
        }, 201))
        resp.set_cookie(
            "access_token", token,
            httponly=True, secure=True, samesite='Lax', max_age=60 * ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return resp
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@user_test.route('/login', methods=['POST'])
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

        resp = make_response(json_kor({
            "message": "로그인 성공!",
            "nickname": user_doc["nickname"],
            "limited_access": user_doc.get("limited_access", False)
        }))
        resp.set_cookie(
            "access_token", token,
            httponly=True, secure=True, samesite='Lax', max_age=60 * ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return resp
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@user_test.route('/logout', methods=['POST'])
def logout():
    resp = make_response(json_kor({"message": "로그아웃되었습니다."}))
    resp.set_cookie("access_token", "", expires=0)
    return resp

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return json_kor({"error": "쿠키에 토큰이 없습니다."}, 401)
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload["user_id"]
            user = db.user.find_one({"_id": ObjectId(user_id)})
            if not user:
                return json_kor({"error": "사용자를 찾을 수 없습니다."}, 404)
            request.user = user
            request.user_id = str(user["_id"])  # 다른 라우터에서도 사용 가능
        except jwt.ExpiredSignatureError:
            return json_kor({"error": "토큰이 만료되었습니다."}, 401)
        except jwt.InvalidTokenError:
            return json_kor({"error": "유효하지 않은 토큰입니다."}, 401)
        return f(*args, **kwargs)
    return decorated

@user_test.route('/update', methods=['PATCH'])
@token_required
def update_user():
    try:
        user_id = request.user["_id"]
        data = request.get_json()

        update_fields = {k: v for k, v in data.items() if k in ['nickname', 'age', 'gender', 'address', 'phone']}
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
