from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB 연결
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://<username>:<password>@<cluster>.mongodb.net/')
client = MongoClient(MONGO_URI)
db = client['maeum_sailing']
letters_collection = db['letters']

@app.route('/')
def home():
    return 'Hello, this is the letter app connected to MongoDB!'

# ✅ 연결 테스트용 라우트
@app.route('/check_db')
def check_db():
    try:
        collections = db.list_collection_names()
        return jsonify({
            "status": "success",
            "message": "MongoDB 연결 성공",
            "collections": collections
        })
    except Exception as e:
        return jsonify({
            "status": "fail",
            "message": "MongoDB 연결 실패",
            "error": str(e)
        })

# 기존 편지 저장 API
@app.route('/write_letter', methods=['POST'])
def write_letter():
    data = request.get_json()
    letter = {
        "sender_id": data.get("sender_id"),
        "emotion": data.get("emotion"),
        "question": data.get("question"),
        "content": data.get("content"),
        "created_at": datetime.utcnow(),
        "receiver_type": data.get("receiver_type"),
        "reply_status": "unanswered"
    }
    letters_collection.insert_one(letter)
    return jsonify({"msg": "Letter saved successfully!"}), 201

if __name__ == '__main__':
    app.run()
