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
from routes.question import question_bp 
from routes.satisfaction_routes import satisfaction_bp

# JWT 인증 데코레이터 (Authorization 헤더 사용)
def token_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return json_kor({"error": "Authorization 헤더가 필요합니다."}, 401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = db.user.find_one({"_id": ObjectId(payload["user_id"])})
            if not user:
                raise jwt.InvalidTokenError
            request.user = user
            request.user_id = str(user["_id"])
        except jwt.ExpiredSignatureError:
            return json_kor({"error": "토큰이 만료되었습니다."}, 401)
        except jwt.InvalidTokenError:
            return json_kor({"error": "유효하지 않은 토큰입니다."}, 401)

        return f(*args, **kwargs)
    return decorated

def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    # ✅ CORS 전체 허용
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    app.config['SWAGGER'] = {
    'title': '마음의 항해 API 문서',
    'uiversion': 3
}

    # ✅ Swagger 설정
    swagger_config = {
        "headers": [],
        "specs": [{
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "마음의 항해 API 문서",
            "description": "JWT 기반 인증이 필요한 API를 테스트할 수 있습니다.",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Bearer <JWT 토큰> 형식으로 입력하세요"
            }
        },
        "security": [{"Bearer": []}]
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # ✅ 루트 확인용 라우트 추가
    @app.route('/', methods=['GET'])
    def root():
        return '마음의 항해 백엔드가 정상 작동 중입니다.'

    # ✅ 블루프린트 등록
    app.register_blueprint(user_test, url_prefix="/api/users")
    app.register_blueprint(reward_routes, url_prefix="/reward")
    app.register_blueprint(item_routes, url_prefix="/item")
    app.register_blueprint(letter_routes, url_prefix="/letter")
    app.register_blueprint(question_bp, url_prefix="/question") 
    app.register_blueprint(satisfaction_bp, url_prefix="/satisfaction")


    # ✅ 보호된 API 예시
    @app.route("/api/users/protected", methods=["GET"])
    @token_required
    def protected():
        user = request.user
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
