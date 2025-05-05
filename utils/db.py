from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Mongo URI는 .env에서 불러옴
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI가 .env에 설정되지 않았습니다.")

# MongoDB 클라이언트 생성
client = MongoClient(MONGO_URI)
db = client.get_default_database()  # 기본 데이터베이스 사용
