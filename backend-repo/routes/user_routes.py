from flask import request, jsonify
from utils.db import db

@user_routes.route('/api/users/signup', methods=['POST'])
def signup():
    data = request.get_json()
    nickname = data.get('nickname')
    age = data.get('age')
    gender = data.get('gender')
    address = data.get('address')
    phone = data.get('phone')

    if not nickname or age is None or not gender:
        return jsonify({"error": "닉네임, 나이, 성별은 필수입니다."}), 400

    if db.users.find_one({"nickname": nickname}):
        return jsonify({"error": "이미 존재하는 닉네임입니다."}), 400

    # 선택 항목 미입력 시 제한 여부 플래그 설정
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

    db.users.insert_one(new_user)
    return jsonify({
        "message": "회원가입 성공!",
        "limited_access": limited_access
    }), 201

@user_routes.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    nickname = data.get('nickname')

    if not nickname:
        return jsonify({"error": "닉네임을 입력해주세요."}), 400

    user = db.users.find_one({"nickname": nickname})
    if not user:
        return jsonify({"error": "해당 닉네임의 사용자가 존재하지 않습니다."}), 404

    token = jwt.encode(
        {"user_id": str(user["_id"]), "nickname": user["nickname"]},
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )

    return jsonify({
        "message": "로그인 성공!",
        "token": token,
        "nickname": user["nickname"],
        "limited_access": user.get("limited_access", False)
    }), 200
