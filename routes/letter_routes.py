from flask import Blueprint, request, Response
from utils.db import db
import uuid
import random
from datetime import datetime
import os
import json

from openai import OpenAI

letter_routes = Blueprint('letter_routes', __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json",
        status=status
    )

AI_REPLY_POOL = [
    "지금도 충분히 잘하고 있어요.",
    "당신의 감정을 이해해요. 같이 이겨내봐요.",
    "조금만 쉬어가도 괜찮아요.",
    "당신은 혼자가 아니에요.",
    "그 마음, 충분히 소중해요."
]

def generate_ai_replies_with_gpt(content):
    prompt = f"""
    아래는 사용자가 쓴 편지입니다:

    "{content}"

    이 편지에 따뜻하게 공감하고 위로하는 짧은 답장을 3개 생성해주세요.
    각 답장은 1~2문장 이내로 해주시고, 존댓말을 사용해주세요.
    너무 유사한 표현은 피해주세요.
    JSON 배열 형식으로 아래처럼 반환해주세요:

    ["답장1", "답장2", "답장3"]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 따뜻한 답장을 잘 쓰는 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85
        )
        ai_text = response.choices[0].message.content
        return json.loads(ai_text.strip())
    except Exception as e:
        print("❌ AI 생성 실패:", e)
        return random.sample(AI_REPLY_POOL, 3)

# 편지 전송
@letter_routes.route('/letter/send', methods=['POST'])
def send_letter():
    data = request.get_json()
    sender_id = data.get("from")
    to_type = data.get("to")
    content = data.get("content")

    if not (sender_id and content and to_type):
        return json_kor({"error": "필수 정보 누락"}), 400

    if to_type == "self":
        receiver_id = sender_id
    elif to_type == "volunteer":
        receiver_id = "volunteer_user"
    elif to_type == "random":
        today = datetime.now().date()
        received_today = db.letter.find({
            "created_at": {"$gte": datetime(today.year, today.month, today.day)},
            "to": {"$ne": "volunteer_user"}
        }).distinct("to")
        all_users = db.user.distinct("_id")
        candidates = [u for u in all_users if str(u) not in received_today and str(u) != sender_id]
        if not candidates:
            return json_kor({"error": "오늘 받을 수 있는 사용자가 없습니다."}, 400)
        receiver_id = random.choice(candidates)
    else:
        return json_kor({"error": "유효하지 않은 수신자 타입입니다."}), 400

    ai_replies = generate_ai_replies_with_gpt(content)

    letter = {
        "_id": str(uuid.uuid4()),
        "from": sender_id,
        "to": receiver_id,
        "content": content,
        "status": "sent",
        "ai_replies": ai_replies,
        "created_at": datetime.now()
    }
    db.letter.insert_one(letter)

    return json_kor({
        "message": "편지 전송 완료!",
        "letter_id": letter["_id"],
        "receiver": receiver_id,
        "ai_replies": ai_replies
    }, 201)

# 편지 답장

@letter_routes.route('/letter/random', methods=['GET'])
@token_required
def has_new_random_letter():
    """
    나에게 새로 온 랜덤 편지가 있는지 여부만 반환 (5초마다 폴링용)
    """
    try:
        user_id = request.user_id
        exists = db.letter.count_documents({
            "to": user_id,
            "from": {"$nin": ["volunteer_user", user_id]},
            "status": "sent"
        }) > 0

        return json_kor({"has_new": exists}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)
    
@letter_routes.route('/letter/my-unread', methods=['GET'])
@token_required
def get_my_unread_letters():
    """
    내가 아직 답장하지 않은 랜덤 편지 목록 조회
    """
    try:
        user_id = request.user_id
        letters = list(db.letter.find(
            {
                "to": user_id,
                "from": {"$nin": ["volunteer_user", user_id]},
                "status": "sent"
            },
            {
                "_id": 1,
                "from": 1,
                "content": 1,
                "ai_replies": 1,
                "created_at": 1
            }
        ).sort("created_at", -1))

        return json_kor({"unread_letters": letters}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)

@letter_routes.route('/letter/reply', methods=['POST'])
def reply_letter():
    data = request.get_json()
    letter_id = data.get("letter_id")
    selected_reply = data.get("selected_reply")

    if not (letter_id and selected_reply):
        return json_kor({"error": "letter_id와 selected_reply는 필수입니다."}), 400

    letter = db.letter.find_one({"_id": letter_id})
    if not letter:
        return json_kor({"error": "해당 편지를 찾을 수 없습니다."}), 404

    if letter.get("status") == "replied":
        return json_kor({"error": "이미 답장이 완료된 편지입니다."}), 400

    db.letter.update_one(
        {"_id": letter_id},
        {"$set": {
            "reply": selected_reply,
            "status": "replied",
            "replied_at": datetime.now()
        }}
    )

    return json_kor({
        "message": "답장이 전송되었습니다.",
        "reply": selected_reply
    }, 200)

@letter_routes.route('/letter/replied-to-me', methods=['GET'])
@token_required
def get_replied_letters_to_me():
    """
    내가 보낸 편지 중, 답장이 달린 편지 목록 반환
    (수동 답장 + AI 자동 답장 포함)
    """
    try:
        user_id = request.user_id
        letters = list(db.letter.find(
            {
                "from": user_id,
                "status": { "$in": ["replied", "auto_replied"] }
            },
            {
                "_id": 1,
                "to": 1,
                "reply": 1,
                "replied_at": 1,
                "content": 1,
                "status": 1
            }
        ).sort("replied_at", -1))

        return json_kor({"replied_letters": letters}, 200)
    except Exception as e:
        return json_kor({"error": str(e)}, 500)


@letter_routes.route('/letter/auto-reply', methods=['POST'])
def auto_reply_to_old_letters():
    """
    24시간 이상 지난 미답장 편지에 대해 AI가 자동 답장 생성
    """
    try:
        threshold = datetime.now() - datetime.timedelta(hours=24)

        # 조건에 맞는 편지 찾기
        expired_letters = list(db.letter.find({
            "status": "sent",
            "created_at": {"$lte": threshold},
            "to": {"$nin": ["volunteer_user"]}
        }))

        auto_replied = []

        for letter in expired_letters:
            # 랜덤으로 AI 답변 선택
            ai_replies = letter.get("ai_replies", [])
            selected_reply = random.choice(ai_replies) if ai_replies else random.choice(AI_REPLY_POOL)

            # 답장 처리
            db.letter.update_one(
                {"_id": letter["_id"]},
                {"$set": {
                    "reply": selected_reply,
                    "status": "auto_replied",
                    "replied_at": datetime.now()
                }}
            )
            auto_replied.append(str(letter["_id"]))

        return json_kor({
            "message": f"{len(auto_replied)}건의 편지에 자동 답장이 생성되었습니다.",
            "auto_replied_ids": auto_replied
        }, 200)

    except Exception as e:
        return json_kor({"error": str(e)}, 500)
