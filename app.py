from flask import Flask, request, jsonify
from pymongo import MongoClient
import os  # os 추가

app = Flask(__name__)

# 환경변수로 MongoDB URI 가져오기
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['letter_app']
letters_collection = db['letters']

@app.route('/')
def home():
    return 'Hello, this is the letter app connected to MongoDB!'
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