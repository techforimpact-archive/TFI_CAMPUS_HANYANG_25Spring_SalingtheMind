# 마음의 항해 (Sailing of the Heart)
**AI 기반 자기표현 글쓰기 조력 및 정서 지원 플랫폼**  

---

## 🌊 Project Overview
### 🫂 협업단체 (Organizations)
본 프로젝트는 2025-1 카카오임팩트 × 테크포임팩트 캠퍼스 프로그램의 지원을 받아, 관계의 회복을 돕는 소셜벤처 사단법인 온기와 함께 ‘돕는 기술’을 지향하는 정서 지원 플랫폼을 개발하였습니다.

### 🎯 목적 (Purpose)
- 감정 표현이 어려운 청소년을 위한 **정서 지원 플랫폼**
- **AI 유도 질문**과 감정 선택 기반 글쓰기로 진입 장벽 최소화
- **편지 전달 및 응답 시스템**을 통해 정서적 연결 제공
- **게임화된 UI와 보상 시스템**을 통해 자발적 사용 유도

### 📱 서비스 소개 (Service Summary)
**『마음의 항해』**는 감정 표현에 어려움을 겪는 청소년을 위한 AI 기반 편지 작성 웹서비스입니다.
사용자가 감정을 선택하면, AI가 맞춤형 질문을 제안하고 글쓰기를 유도하여,
자기표현의 진입장벽을 낮추고 정서적 연결과 회복 경험을 제공합니다.

---

## 🧑‍🤝‍🧑 Team Members

| Name | Affiliation | Role | Responsibility | Contact |
|------|------|------|----------------|---------|
| **유서현 (Seohyeon Yoo)** | DataScience | 리더 (PM) | "" | ✉️ dbtjgus6988@gmail.com<br>🔗 [GitHub](https://github.com/dbtjgus6988) |
| **이예진 (Yejin Lee)** | ComputerScience | 프론트엔드 개발자 | "" | ✉️ clarecse02@gmail.com<br>🔗 [GitHub](https://github.com/lwjmcn) |
| **한채린 (Chaelin Han)** | InformationSystem | 백엔드 개발자 | "" | ✉️ chelin02@naver.com<br>🔗 [GitHub](https://github.com/han-chaelin) |
| **김혜연 (Hyeyeon Kim)** | DataScience | 백엔드 개발자 | "" | ✉️ rbanbla@hanyang.ac.kr<br>🔗 [GitHub](https://github.com/rbanbla) |
| **임선민 (Sunmin Lim)** | InformationSystem | UI 디자이너 | "" | ✉️ imsnmn24@gmail.com<br>🔗 [GitHub](https://github.com/Sunmin-Lim) |

---
## 🧩 Key Features & UI Overview
🏝 메인 화면
- 캐릭터 ‘온달’이 감정 표현과 지속 활동을 돕는 서포터
- 획득한 아이템으로 공간 커스터마이징

🎁 리워드 시스템
- 편지/답장 작성 시 포인트 지급
- 일정 포인트 달성 시 레벨업 및 꾸미기 아이템 획득

🌊 바다 (편지 읽기/답장 공간)
- 익명 편지 열람
- 랜덤 전송된 익명 편지 답장 가능

📮 우체국 (편지 작성 공간)
- 수신자 선택 → 감정 선택 → AI 기반 질문으로 편지 작성 유도 → 편지 작성
- 자가 보관/익명 전송/온기우체부 전송 선택 가능

---
## ⚙️ Technical Implementation

### 🧩 시스템 아키텍처
#### 아키텍처 다이어그램
```plaintext
┌────────────────────────────────────────────────────────────────────┐
│                            Frontend                                │
├────────────────────────────────────────────────────────────────────┤
│  UI Interface             |  State Management & Routing            │
│  • Mobile Web + CSS       |  • Zustand + React Router              │
└───────────────────────────┴────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│                            Backend                                 │
├────────────────────────────────────────────────────────────────────┤
│  Auth & Routing           |  Business Logic                        │
│  • JWT + Flask            |  • Emotion Analysis + Question Gen.    │
│                                                                    │
│  API Communication        |  Database                              │
│  • Axios + REST API       |  • MongoDB                             │
└───────────────────────────┴────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│                            AI Service                              │
├────────────────────────────────────────────────────────────────────┤
│  OpenAI API              |  Prompting                              │
│  • GPT-4o                |  • Emotion-based Question Gen.          │
│                                                                    │
│  Text Processing         |                                         │
│  • Natural Language Processing                                     │
└────────────────────────────────────────────────────────────────────┘
```

#### Frontend
- 사용자 인터페이스: `mobile web + module css`
- 상태 관리 & 라우팅: `Zustand + React Router`
- API 통신: `Axios + REST API`

#### Backend
- 프레임워크: `Flask` – 경량화된 웹 프레임워크로 RESTful API 설계
- 라우팅 & 인증: `JWT Auth` + Flask Blueprint – 사용자 인증 및 기능별 라우터 분리
- 비즈니스 로직:
  - 감정 기반 질문 제시 및 편지 처리
  - GPT API를 활용한 자동 답장 생성
- 데이터베이스: `MongoDB Atlas` – 유연한 비정형 데이터 저장 및 쿼리
- 자동 응답 시스템:  
  - Render의 Background Worker에서 자동응답 대상 편지를 탐색  
  - GPT API 호출 후 응답 저장까지 주기적 처리
- 문서화 도구: `Flasgger` – Swagger 기반 API 명세 자동화

#### AI Service
- GPT-4o API 기반 감정 맞춤 질문 생성
- 사용자 입력 응답 처리 및 텍스트 전처리

### 🤖 Prompting
- 정서적 라포 유도를 위한 GPT 기반 화법 설계
- 공감형 대화체로 감정 반응 유도
- GPT-4o를 활용한 문맥 이해 및 감정 표현 품질 향상

### 🚀 Deployment
- **Frontend**: `Vercel` (자동 배포 및 CDN)
- **Backend**: `Render` (Web Service와 Worker 인스턴스를 분리 배포)
- 
---
## directory structure
-**Frontend**
-**Backend** 
```plaintext
├── routes/                 # API 라우터 정의 모음
│   ├── item_routes.py           # 아이템 관련 API : 아이템 상세조회, 
│   ├── letter_routes.py         # 편지 작성/조회 API
│   ├── reward_routes.py         # 리워드 지급/조회 API
│   ├── satisfaction_routes.py   # 만족도 평가 관련 API
│   ├── user_routes.py           # 회원가입/로그인 등 사용자 API
│   ├── question.py              # 감정 질문 관련 API
│   ├── user_test.py             # 유저 관련 API
│   └── __init__.py
│
├── scripts/               # 초기 데이터 삽입 등 관리용 스크립트
│   └── init_users.py      # 기존 데이터 삭제 및 더미 유저 추가
│
├── utils/                 # 공통 유틸 함수 모음
│   ├── auth.py            # 토큰 유효성
|   ├── config.py          # 환경 변수와 공통 설정을 관리하는 설정 파일
|   ├── db.py              # MongoDB 연결 초기화 및 전역 DB 인스턴스 제공 모듈
|   ├── response.py        # 한글이 포함된 JSON 응답을 UTF-8로 반환하는 유틸 함수
|   └── reward.py          # 보상 제공 유틸 함수 
│
├── app.py                 # Flask 앱 생성 및 라우트 등록
├── auto_reply.py          # GPT 기반 자동 응답 처리 (Render Worker)
├── main.py                # 서버 실행 진입점
├── render.yaml            # Render 배포 설정 파일
├── requirements.txt       # 사용 라이브러리 목록
├── test.http              # HTTP 요청 테스트용 -REST Client 확장
└── README.md
```        

## 🛠 Development Environment

| Category   | Stack / Tool |
|------------|--------------|
| **Frontend** | React + Zustand + Module CSS |
| **Backend** | Flask + JWT + MongoDB |
| **AI Service** | OpenAI GPT-4o API |
| **Deployment** | Vercel (Frontend), Render (Backend) |
| **Others** | Axios, REST API, Notion (Issue Mgmt), GitHub (Version Control) |

---

## 🎓 Fellowship & Mentorship
- **Fellow**: 조현식 님 (온기 Onji) 🔗[Ongibox](https://ongibox.co.kr/)
- **Mentor**: 이정음 님 (카카오 Kakao) 🔗[GitHub](https://github.com/jeongum) 

---

## 📌 Expected Impact
- 감정 표현을 통한 자기 이해 및 정서 회복
- AI 기반 디지털 돌봄 서비스의 가능성 검증
- 교육·심리 분야로의 확장 가능성

---

## 📺 Demo & Resources
- 💻 [서비스 링크 (Demo)](https://gominhanyang.vercel.app/signin)
- 📄 [최종 발표자료 PDF](https://drive.google.com/file/d/1YeNR23y816Cup3twf0RxQrPRHCDIaSAY/view?usp=sharing)
- 📹 [시연 영상](https://drive.google.com/drive/u/0/folders/1PTBSqgeTHN83Uz9GSSe9Z2MQQmFQl-Mn) 

🧵 Troubleshooting
| 문제            | 원인              | 해결 방법                                                       |
| ------------- | --------------- | ----------------------------------------------------------- |
| `bson` 모듈 에러  | MongoDB 드라이버 누락 | `pip install pymongo` 또는 `pip install bson`                 |
| CORS 오류       | 프론트/백엔드 도메인 불일치 | Flask에서 `CORS(app, resources={r"/*": {"origins": "*"}})` 설정 |
| OpenAI API 오류 | 키 누락 또는 요금제 문제  | `.env` 파일에 `OPENAI_API_KEY=your-key` 등록                     |

---
## 🔮 Future Work
- 📱 악성 문구 및 유해 답장 필터링
- 📬 받은 편지 카카오톡 알림 (편지 작성 리마인드 및 답장 도착 알림)
- 📈 정서 회복 성장 여정 시각화 → 임팩트 지표 측정에 활용
- 🧠 위로 글귀 가챠
- 학교 및 복지기관 대상 온기 서비스 시연



