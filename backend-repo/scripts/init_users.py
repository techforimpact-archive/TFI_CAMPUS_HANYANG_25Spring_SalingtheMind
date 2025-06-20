# scripts/reset_db.py
import os, sys

# 1) 프로젝트 루트를 import path에 추가
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from utils.config import DB_NAME

# 환경변수 로드
load_dotenv()

# MongoDB 연결
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME", DB_NAME)]

# ⚠️ 기존 데이터 전부 삭제
for coll in ("letters", "users", "items", "user_items"):
    db[coll].delete_many({})

# 🧪 테스트용 사용자
users = [
    {"_id": ObjectId("615f1f4e2b8a4b3d1cde0001"), "nickname": "마음씨앗", "point": 0, "awarded_thresholds": []},
    {"_id": ObjectId("615f1f4e2b8a4b3d1cde0002"), "nickname": "해맑은별", "point": 0, "awarded_thresholds": []},
    {"_id": ObjectId("615f1f4e2b8a4b3d1cde0003"), "nickname": "푸른해님", "point": 0, "awarded_thresholds": []},
]
db.users.insert_many(users)

# 📦 아이템 카탈로그
items = [
    {"name": "반짝이 편지지", "description": "편지를 꾸밀 수 있는 반짝이 배경지", "image_url": "..."},
    {"name": "샤이니 스티커",  "description": "반짝이는 스티커 세트",     "image_url": "..."},
    {"name": "골드 배지",     "description": "금색 디자인의 특별 배지",  "image_url": "..."},
]
db.items.insert_many(items)

print(f"✅ {db.name} 초기화 완료")
