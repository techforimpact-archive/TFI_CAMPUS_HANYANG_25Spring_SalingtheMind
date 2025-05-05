import os
from flask import Flask, jsonify, request, Response
from bson.objectid import ObjectId
import jwt
from flasgger import Swagger

from utils.config import JWT_SECRET_KEY, JWT_ALGORITHM
from utils.db import db
from routes.user_test import user_test
from routes.reward_routes import reward_routes
from routes.item_routes import item_routes
from routes.letter_routes import letter_routes


def json_kor(data, status=200):
    return Response(
        jsonify(data).data.decode('utf-8'),
        content_type="application/json; charset=utf-8",
        status=status
    )


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
            request.user_id = str(user["_id"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "토큰이 만료되었습니다."}), 401
        except Exception:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401

        return f(*args, **kwargs)

    return decorated


def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지

    # Swagger 초기화
    Swagger(app)

    # Blueprint 등록
    app.register_blueprint(user_test, url_prefix="/api/users")
    app.register_blueprint(reward_routes, url_prefix="/reward")
    app.register_blueprint(item_routes, url_prefix="/item")
    app.register_blueprint(letter_routes, url_prefix="/letter")

    # 예시 보호된 엔드포인트
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
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
