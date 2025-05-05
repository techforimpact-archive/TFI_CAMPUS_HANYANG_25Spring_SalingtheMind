import datetime
from flask import request, jsonify, Blueprint, Response
from flasgger import Swagger, swag_from
import jwt
from bson.objectid import ObjectId

from utils.db import db
from utils.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

user_test = Blueprint('user', __name__, url_prefix='/api/users')


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


@user_test.route('/signup', methods=['POST'])
def signup():
    """
    회원가입
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nickname:
              type: string
              description: 사용자 닉네임
            age:
              type: integer
              description: 나이
            gender:
              type: string
              description: 성별
            address:
              type: string
              description: 주소
            phone:
              type: string
              description: 전화번호
          required:
            - nickname
            - age
            - gender
    responses:
      201:
        description: 회원가입 성공
        schema:
          type: object
          properties:
            message:
              type: string
            token:
              type: string
            nickname:
              type: string
            limited_access:
              type: boolean
      400:
        description: 잘못된 요청
      500:
        description: 서버 에러
    """
    try:
        data = request.get_json()
        nickname = data.get('nickname')
        age      = data.get('age')
        gender   = data.get('gender')
        address  = data.get('address')
        phone    = data.get('phone')

        if not nickname or age is None or not gender:
            return jsonify({"error": "닉네임, 나이, 성별은 필수입니다."}), 400

        if db.user.find_one({"nickname": nickname}):
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

        result = db.user.insert_one(new_user)
        user_doc = db.user.find_one({"_id": result.inserted_id})
        token = create_token(user_doc)

        return jsonify({
            "message": "회원가입 성공!",
            "token": token,
            "nickname": user_doc["nickname"],
            "limited_access": limited_access
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_test.route('/login', methods=['POST'])
def login():
    """
    로그인
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nickname:
              type: string
              description: 사용자 닉네임
          required:
            - nickname
    responses:
      200:
        description: 로그인 성공
        schema:
          type: object
          properties:
            message:
              type: string
            token:
              type: string
            nickname:
              type: string
            limited_access:
              type: boolean
      400:
        description: 닉네임 누락
      404:
        description: 사용자 없음
      500:
        description: 서버 에러
    """
    try:
        data = request.get_json()
        nickname = data.get('nickname')

        if not nickname:
            return jsonify({"error": "닉네임을 입력해주세요."}), 400

        user_doc = db.user.find_one({"nickname": nickname})
        if not user_doc:
            return jsonify({"error": "해당 닉네임의 사용자가 존재하지 않습니다."}), 404

        token = create_token(user_doc)
        return jsonify({
            "message": "로그인 성공!",
            "token": token,
            "nickname": user_doc["nickname"],
            "limited_access": user_doc.get("limited_access", False)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
