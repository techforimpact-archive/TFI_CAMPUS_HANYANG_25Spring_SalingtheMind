# app.py
import os
from flask import Flask, jsonify, request
from bson.objectid import ObjectId
import jwt

from utils.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.db import db
from routes.user_test import user_test      # 기존 user_test → user_routes로 가정
from routes.reward_routes import reward_routes  # 추가
from routes.item_routes import item_routes      # 추가

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "Bearer 토큰이 필요합니다."}), 401

        token = parts[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = db.users.find_one({"_id": ObjectId(payload["user_id"])})
            if not user:
                raise jwt.InvalidTokenError
            request.user_id = str(user["_id"])  # Flask의 request 객체에 유저 ID 저장
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "토큰이 만료되었습니다."}), 401
        except Exception:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401

        return f(*args, **kwargs)
    return decorated

def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False  # 한글 응답 깨짐 방지

    # 블루프린트 등록
    app.register_blueprint(user_test, url_prefix="/api/users")
    app.register_blueprint(reward_routes, url_prefix="/reward")
    app.register_blueprint(item_routes, url_prefix="/item")

    # 테스트용 보호된 API
    @app.route("/api/users/protected", methods=["GET"])
    @token_required
    def protected():
        user = db.users.find_one({"_id": ObjectId(request.user_id)})
        return jsonify({
            "message": f"안녕하세요, {user['nickname']}님!",
            "user_id": str(user["_id"]),
            "limited_access": user.get("limited_access", False)
        })

    return app

if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "development") == "development"
    create_app().run(host="0.0.0.0", port=5000, debug=debug)