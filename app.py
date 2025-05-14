import os
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from bson.objectid import ObjectId
import jwt
from flasgger import Swagger

from utils.config import JWT_SECRET_KEY, JWT_ALGORITHM
from utils.db import db
from routes.user_test import user_test
from routes.reward_routes import reward_routes
from routes.item_routes import item_routes
from routes.letter_routes import letter_routes


# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        jsonify(data).data.decode('utf-8'),
        content_type="application/json; charset=utf-8",
        status=status
    )


# 쿠키 기반 JWT 인증 데코레이터
def token_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return json_kor({"error": "쿠키에 토큰이 없습니다."}, 401)
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = db.user.find_one({"_id": ObjectId(payload["user_id"])})
            if not user:
                raise jwt.InvalidTokenError
            request.user = user
            request.user_id = str(user["_id"])  # 다른 라우터 호환용
        except jwt.ExpiredSignatureError:
            return json_kor({"error": "토큰이 만료되었습니다."}, 401)
        except jwt.InvalidTokenError:
            return json_kor({"error": "유효하지 않은 토큰입니다."}, 401)

        return f(*args, **kwargs)
    return decorated


def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    # ✅ CORS (Render + 프론트 연동용)
    CORS(app, origins=["https://your-frontend.onrender.com"], supports_credentials=True)

    # ✅ Swagger 설정
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"  # <- 여기 접근 가능해야 Swagger 열림
    }
    Swagger(app)
    

    # ✅ 블루프린트 등록
    app.register_blueprint(user_test, url_prefix="/api/users")
    app.register_blueprint(reward_routes, url_prefix="/reward")
    app.register_blueprint(item_routes, url_prefix="/item")
    app.register_blueprint(letter_routes, url_prefix="/letter")

    # ✅ 테스트용 보호된 라우트
    @app.route("/api/users/protected", methods=["GET"])
    @token_required
    def protected():
        user = db.user.find_one({"_id": ObjectId(request.user_id)})
        return jsonify({
            "message": f"안녕하세요, {user['nickname']}님!",
            "user_id": str(user["_id"]),
            "limited_access": user.get("limited_access", False)
        })

    return app
app = create_app()
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
