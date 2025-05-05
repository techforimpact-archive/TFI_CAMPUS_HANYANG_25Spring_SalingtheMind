## letters api 테스트 할 때 토큰이 필요해서 일단은 테스트 용으로 회원가입이랑 로그인 등등 만들어 보았습니당...
##토큰 발급 안하면 빼두 돼여

import datetime
from flask import request, jsonify, Blueprint
import jwt
from bson.objectid import ObjectId

from utils.db import db
from utils.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

user_test = Blueprint('user', __name__)

def create_token(user_doc):
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "user_id": str(user_doc["_id"]),
        "nickname": user_doc["nickname"],
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

@user_test.route('signup', methods=['POST'])
def signup():
    data = request.get_json()
    nickname = data.get('nickname')
    age      = data.get('age')
    gender   = data.get('gender')
    address  = data.get('address')
    phone    = data.get('phone')

    if not nickname or age is None or not gender:
        return jsonify({"error": "닉네임, 나이, 성별은 필수입니다."}), 400

    if db.user.find_one({"nickname": nickname}):  # ← 수정
        return jsonify({"error": "이미 존재하는 닉네임입니다."}), 400

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

    result = db.user.insert_one(new_user)  # ← 수정
    user_doc = db.user.find_one({"_id": result.inserted_id})  # ← 수정
    token = create_token(user_doc)

    return jsonify({
        "message": "회원가입 성공!",
        "token": token,
        "nickname": user_doc["nickname"],
        "limited_access": limited_access
    }), 201

@user_test.route('login', methods=['POST'])
def login():
    data = request.get_json()
    nickname = data.get('nickname')

    if not nickname:
        return jsonify({"error": "닉네임을 입력해주세요."}), 400

    user_doc = db.user.find_one({"nickname": nickname})  # ← 수정
    if not user_doc:
        return jsonify({"error": "해당 닉네임의 사용자가 존재하지 않습니다."}), 404

    token = create_token(user_doc)
    return jsonify({
        "message": "로그인 성공!",
        "token": token,
        "nickname": user_doc["nickname"],
        "limited_access": user_doc.get("limited_access", False)
    }), 200
