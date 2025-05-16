from flask import Blueprint, request, Response
from utils.db import db
from utils.auth import token_required
from routes.reward_routes import grant_point_by_action
import uuid
import random
import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from flasgger import swag_from
from bson import ObjectId



letter_routes = Blueprint('letter_routes', __name__, url_prefix='/letter')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 한글 JSON 응답 헬퍼
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8",
        status=status
    )
def get_nickname(user_id):
    try:
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        user = db.user.find_one({"_id": user_id}, {"nickname": 1})
        return user.get("nickname", "알 수 없음") if user else "알 수 없음"
    except Exception:
        return "알 수 없음"
      
# AI fallback pool
AI_REPLY_POOL = [
    "지금도 충분히 잘하고 있어요.",
    "당신의 감정을 이해해요. 같이 이겨내봐요.",
    "조금만 쉬어가도 괜찮아요.",
    "당신은 혼자가 아니에요.",
    "그 마음, 충분히 소중해요."
]
QUESTION_POOL = [
    "이 상황에서 가장 먼저 떠오르는 감정은 무엇인가요?",
    "지금 이 순간, 어떤 생각이 가장 크게 와 닿나요?",
    "이 편지를 통해 얻고 싶은 위로는 무엇인가요?",
    "최근 비슷한 경험을 한 적이 있나요? 어떤 느낌이었나요?",
    "이 상황에서 스스로에게 해주고 싶은 조언은 무엇인가요?"
]

# GPT 헬퍼 함수
def generate_title_with_gpt(content):
    prompt = f"""
아래는 사용자가 쓴 편지 내용입니다:
"{content}"

이 편지의 내용을 함축적으로 잘 요약하고 있는 짧은 제목을 1개 생성해주세요.
10자 이내로, 핵심 키워드를 담아 응답해주세요.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 감성적인 제목을 잘 만드는 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=16
        )
        return response.choices[0].message.content.strip().strip('"')
    except Exception:
        return content[:10]
def generate_ai_replies_with_gpt(content: str, mode: str = 'assist') -> list:
    """
    주어진 편지 내용을 바탕으로 질문 또는 답장을 생성합니다.

    mode:
        - 'assist': 공감 기반 질문 3개 생성 (답장 옵션)
        - 'ai': 캐릭터 '온기'의 공감 위주 답장 생성 (자동 답장)
    """
    if not content or len(content.strip()) < 10:
        # 내용이 비정상적으로 짧으면 fallback으로 돌림
        return random.sample(QUESTION_POOL if mode == 'assist' else AI_REPLY_POOL, 3 if mode == 'assist' else 1)

    try:
        if mode == 'assist':
            prompt = f"""
        아래는 누군가가 쓴 편지입니다:
\"{content}\"

이 편지를 읽고 공감하며 답장에 도움이 되는 질문 3개를 만들어주세요.
각 질문은 1문장 이내이며, 예의 바르고 부드럽게 작성해주세요.
결과는 JSON 배열 형식으로 반환해주세요.

예시:
["어떤 점이 가장 힘들게 느껴지셨나요?", "그 상황에서 위로가 되었던 것이 있었나요?", "앞으로 어떤 변화가 생기길 바라시나요?"]
"""
        elif mode == 'ai':
            prompt = f"""
아래는 누군가가 쓴 편지입니다:
\"{content}\"

이 편지를 읽고, 캐릭터 '온기'가 따뜻하게 공감하며 위로의 답장을 작성하려고 합니다.
답장은 존댓말로, 공감 위주의 따뜻한 말 2~3문장으로 작성해주세요.
"""
        else:
            return []

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )

        result = response.choices[0].message.content.strip()

        import json
        if mode == 'assist':
            # 질문 리스트 반환
            questions = json.loads(result)
            return questions if isinstance(questions, list) else []
        else:
            # 단일 답장 텍스트 반환
            return result

    except Exception as e:
        print(f"[GPT 실패] {mode} 질문/답장 생성 실패: {e}")
        return random.sample(QUESTION_POOL if mode == 'assist' else AI_REPLY_POOL, 3 if mode == 'assist' else 1)

@letter_routes.route('/send', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Letter'],
    'summary': '편지 전송',
    'description': '수신 타입(to)에 따라 수신자를 자동으로 결정하고, 본문과 감정을 포함하여 편지를 전송합니다.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'to': {'type': 'string', 'description': '수신 타입 (self, volunteer, random)'},
                    'content': {'type': 'string', 'description': '편지 내용'},
                    'emotion': {'type': 'string', 'description': '감정 태그'}
                },
                'required': ['to', 'content', 'emotion']
            }
        }
    ],
    'responses': {
        201: {'description': '전송 성공'},
        400: {'description': '필수 정보 누락 또는 유효하지 않은 수신 타입'},
        500: {'description': '서버 에러'}
    }
})
def send_letter():
    data = request.get_json() or {}
    sender = ObjectId(request.user_id)
    to_type = data.get("to")
    content = data.get("content")
    emotion = data.get("emotion")
    if not (to_type and content and emotion):
        return json_kor({"error": "필수 정보 누락"}, 400)
    
    # 1000자 글자수 제한
    if len(content) > 1000:
        return json_kor({"error": "편지는 최대 1000자까지 작성할 수 있습니다."}, 400)
    
    # 200자 초과 포인트 지급
    if len(content) > 200:
        grant_point_by_action(sender, "long_letter_bonus")

    # 수신자 결정
    if to_type == 'self':
        receiver = sender
    elif to_type == 'volunteer':
        receiver = 'volunteer'
    elif to_type == 'random':
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        users = db.user.distinct('_id')
        candidates = [u for u in users if u != sender]
        if not candidates:
            return json_kor({"error": "오늘 받을 수 있는 사용자가 없습니다."}, 400)
        receiver = random.choice(candidates)
    else:
        return json_kor({"error": "유효하지 않은 수신 타입"}, 400)
    title = generate_title_with_gpt(content)
    letter = {"_id": ObjectId(uuid.uuid4()), "from": sender, "to": receiver, "title": title,"emotion": emotion, "content": content, "status": 'sent',
              "saved": to_type in ['self', 'volunteer'], "created_at": datetime.now()}
    db.letter.insert_one(letter)
    return json_kor({"message": "편지 전송 완료", "letter_id": letter['_id'],
                     "to": get_nickname(receiver), "title": title, "emotion": emotion}, 201)

@letter_routes.route('/random', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Letter'],
    'summary': '나에게 온 미답장 편지 목록 조회',
    'responses': {
        200: {'description': '미답장 편지 목록 반환'},
        500: {'description': '서버 에러'}
    }
})

def get_my_unread_letters():
    user = ObjectId(request.user_id)
    letters = list(db.letter.find({"to": user, "status": 'sent', "from": {"$nin": ['volunteer_user', user]}},{'_id': 1, 'from': 1, 'title': 1, 'emotion': 1, 'created_at': 1}).sort('created_at', -1))
    for letter in letters:
          letter['from_nickname'] = get_nickname(letter['from'])
    return json_kor({"unread_letters": letters}, 200)


@letter_routes.route('/<letter_id>', methods=['GET'])
@token_required
def get_letter_detail(letter_id):
    """
    편지 상세 조회 (및 자동 저장/댓글 읽음 처리)
    ---
    tags:
      - Letter
    parameters:
      - name: letter_id
        in: path
        type: string
        required: true
        description: 조회할 편지의 ID
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer 토큰
    responses:
      200:
        description: 편지 상세 조회 성공
        schema:
          type: object
          properties:
            letter:
              type: object
              properties:
                _id:
                  type: string
                from:
                  type: string
                to:
                  type: string
                title:
                  type: string
                emotion:
                  type: string
                content:
                  type: string
                created_at:
                  type: string
                saved:
                  type: boolean
                status:
                  type: string
            comments:
              type: array
              items:
                type: object
                properties:
                  _id:
                    type: string
                  from:
                    type: string
                  content:
                    type: string
                  read:
                    type: boolean
                  created_at:
                    type: string
      404:
        description: 편지를 찾을 수 없음
      500:
        description: 서버 오류
    """
    user = ObjectId(request.user_id)
    letter = db.letter.find_one(
        {"_id":  ObjectId(letter_id)},
        {'_id': 1, 'from': 1, 'to': 1, 'title': 1, 'emotion': 1, 'content': 1, 'created_at': 1, 'saved': 1, 'status': 1}
    )
    if not letter:
        return json_kor({"error": "편지를 찾을 수 없습니다."}, 404)
      
    if letter['from'] != user and letter['to'] != user:
      return json_kor({"error": "해당 편지에 접근할 권한이 없습니다."}, 403)
    letter['from_nickname'] = get_nickname(letter['from'])
    letter['to_nickname'] = get_nickname(letter['to'])

    result = {'letter': letter}

    # ✅ 편지를 저장 처리할 조건
    is_random_to_me = (
        letter['to'] == user and
        letter['from'] != user and
        letter['to'] != 'volunteer_user' and
        not letter.get('saved', False)
    )
    if is_random_to_me:
        db.letter.update_one({'_id': letter_id}, {'$set': {'saved': True}})
        letter['saved'] = True  # 반환값에도 반영

    # 댓글 처리
    is_random_reply = (
        letter['to'] == user and
        letter['from'] != user and
        letter['status'] in ['replied', 'auto_replied']
    )
    if is_random_reply:
        comments = list(db.comment.find(
            {'original_letter_id':  ObjectId(letter_id)},
            {'_id': 1, 'from': 1, 'content': 1, 'read': 1, 'created_at': 1}
        ).sort('created_at', 1))
        
        result['comments'] = comments

        unread_ids = [ObjectId(c['_id']) for c in comments if not c.get('read')]
        
        for comment in comments:
          comment['from_nickname'] = get_nickname(comment['from'])
        
        if unread_ids:
            db.comment.update_many(
                {'_id': {'$in': unread_ids}},
                {'$set': {'read': True}}
            )

    return json_kor(result, 200)


@letter_routes.route('/reply-options', methods=['GET'])
@token_required
def get_reply_options():
    """
    AI 질문 3개 생성 (답장 옵션)
    ---
    tags:
      - Letter
    parameters:
      - name: letter_id
        in: query
        type: string
        required: true
        description: 편지 ID
    responses:
      200:
        description: 성공
      404:
        description: 편지 없음
    """
    lid = ObjectId(request.args.get('letter_id'))
    
    letter = db.letter.find_one({'_id': lid})
    if not letter:
        return json_kor({'error': '편지를 찾을 수 없습니다.'}, 404)
    questions = generate_ai_replies_with_gpt(letter.get('content', ''), 'assist')
    return json_kor({'questions': questions}, 200)

@letter_routes.route('/reply', methods=['POST'])
@token_required
def reply_letter():
    """
    유저 답장 저장
    ---
    tags:
      - Letter
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            letter_id:
              type: string
            reply:
              type: string
          required: [letter_id, reply]
    responses:
      200:
        description: 답장 성공
      400:
        description: 잘못된 요청
    """
    data = request.get_json() or {}
    lid = ObjectId(data.get('letter_id'))
    text = data.get('reply')
    if not (lid and text):
        return json_kor({'error': '필수값 누락'}, 400)

    # 1000자 글자수 제한한
    if len(text) > 1000:
        return json_kor({'error': '답장은 최대 1000자까지 작성할 수 있습니다.'}, 400)
    
    # 200자 초과 포인트 지급
    if len(text) > 200:
        grant_point_by_action(ObjectId(request.user_id), "long_letter_bonus")

    orig = db.letter.find_one({'_id': lid})
    if not orig or orig.get('status') != 'sent':
        return json_kor({'error': '답장할 수 없습니다.'}, 400)
    comment = {'_id': ObjectId(uuid.uuid4()), 'from': request.user_id,'to': orig.get('from'), 'content': text, 'read': False,'created_at': datetime.now(), 'original_letter_id': lid}
    db.comment.insert_one(comment)
    db.letter.update_one({'_id': lid}, {'$set': {'status': 'replied', 'replied_at': datetime.now()}})
    return json_kor({'message': '답장 완료'}, 200)

@letter_routes.route('/replied-to-me', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Letter'],
    'summary': '내가 받은 편지 중 답장 완료된 목록 조회',
    'responses': {
        200: {
            'description': '답장 완료된 편지 목록 반환',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'replied-to-me': {
                                'type': 'array',
                                'items': {'type': 'object'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_replied_letters_to_me():
    user = ObjectId(request.user_id)
    letters = list(db.letter.find({
        'to': user,
        'from': {'$ne': user},
        'status': {'$in': ['replied', 'auto_replied']}
    }, {
        '_id': 1, 'from': 1, 'title': 1, 'emotion': 1, 'content': 1,
        'status': 1, 'replied_at': 1
    }).sort('replied_at', -1))
    for letter in letters:
        letter['from_nickname'] = get_nickname(letter['from'])
    return json_kor({'replied-to-me': letters}, 200)

@letter_routes.route('/for-letter/<letter_id>', methods=['GET'])
@token_required
def get_comments_for_letter(letter_id):
    """
    특정 편지의 댓글 목록 조회
    ---
    tags:
      - Letter
    parameters:
      - name: letter_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 성공
    """
    
    comms = list(db.comment.find({'original_letter_id': str(letter_id)},{'_id':1,'from':1,'content':1,'created_at':1,'read':1}).sort('created_at', -1))
    for comment in comms:
        comment['from_nickname'] = get_nickname(comment['from'])
    
    return json_kor({'comments': comms}, 200)

@letter_routes.route('/auto-reply', methods=['POST'])
def auto_reply_to_old_letters():
    """
    24시간 지난 랜덤 편지 자동 답장
    ---
    tags:
      - Letter
    responses:
      200:
        description: 자동 답장 결과
    """
    threshold = datetime.now() - timedelta(hours=24)
    expired = list(db.letter.find({'status': 'sent', 'created_at': {'$lte': threshold},'to': {'$nin': ['volunteer_user']},'$expr': {'$ne': ['$to', '$from']}}))
    auto_ids = []
    for mail in expired:
        ai_list = generate_ai_replies_with_gpt(mail.get('content', ''), 'ai')
        reply = random.choice(ai_list) if isinstance(ai_list, list) else ai_list
        cm = {'_id': str(uuid.uuid4()), 'from': '온기', 'to': mail.get('from'),'content': reply, 'read': False, 'created_at': datetime.now(),'original_letter_id': mail.get('_id')}
        db.comment.insert_one(cm)
        db.letter.update_one({'_id': mail.get('_id')}, {'$set': {'status': 'auto_replied', 'replied_at': datetime.now()}})
        auto_ids.append(mail.get('_id'))
        cm['to_nickname'] = get_nickname(cm['from'])
    return json_kor({'message': f"{len(auto_ids)}건 자동 답장 완료", 'auto_ids': auto_ids}, 200)

@letter_routes.route('/saved', methods=['GET'])
@token_required
def get_saved_letters():
    """
    내가 저장한 편지 목록 조회
    ---
    tags:
      - Letter
    responses:
      200:
        description: 성공
    """
    user = ObjectId(request.user_id)
    letters = list(db.letter.find({'from': user, 'saved': True},{'_id':1,'from':1,'title':1,'emotion':1,'created_at':1,'to':1}).sort('created_at', -1))
    for letter in letters:
        letter['from_nickname'] = get_nickname(letter['from'])
        letter['to_nickname'] = get_nickname(letter['to'])
    return json_kor({'saved_letters': letters}, 200)
