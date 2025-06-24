# 🌊 마음의 항해 (Sailing of the Heart)
<img width="196" alt="image" src="![임시 메인 이미지](attachment:c58b5ed0-d633-4959-aadf-4bbd22196c5f:IMG_4145.jpeg)" /><br>
본 프로젝트는 2025-1 카카오임팩트 × 테크포임팩트 캠퍼스 프로그램의 지원을 받아, 관계의 회복을 돕는 소셜벤처 사단법인 온기와 함께 ‘돕는 기술’을 지향하는 **AI 기반 자기표현 글쓰기 조력 및 정서 지원 플랫폼**을 개발하였습니다.<br>
🔗 [서비스 링크(Live Demo)](https://gominhanyang.vercel.app/signin)
(⚠️ 본 서비스는 모바일 환경에 최적화되어 있습니다. PC가 아닌 스마트폰으로 접속해 주세요!)

---

## Project Overview
### 프로젝트 소개
『마음의 항해』는 감정 표현에 어려움을 겪는 청소년을 위한 AI 기반 편지 작성 웹서비스입니다. 사용자가 감정을 선택하면, AI가 맞춤형 질문을 제안하고 글쓰기를 유도하여, 자기표현의 진입장벽을 낮추고 정서적 연결과 회복 경험을 제공합니다.
- 감정 표현이 어려운 청소년을 위한 **정서 지원 플랫폼**
- **AI의 유도 질문**과 감정 선택 기반 글쓰기로 진입 장벽 최소화
- **편지 전송** 및 **답장** 시스템을 통해 정서적 연결 제공
- **게임화된 UI**와 **보상 시스템**을 통해 자발적 사용 유도

### 프로젝트 결과 (Resources)
📄 [최종 발표자료 PDF](https://drive.google.com/file/d/1YeNR23y816Cup3twf0RxQrPRHCDIaSAY/view?usp=sharing)
📹 [시연 영상](https://drive.google.com/drive/u/0/folders/1PTBSqgeTHN83Uz9GSSe9Z2MQQmFQl-Mn) 

---

## Team Members

| Role | Name | Affiliation | Responsibility | Contact |
|------|------|------|----------------|---------|
| PM(리더) | **유서현 (Seohyeon Yoo)** | DataScience | - 프로젝트 기획 및 총괄<br>- UI/UX 설계 및 디자인 주도<br>- 유저테스트 담당<br>- 논문 작성 및 발표 | ✉️ dbtjgus6988@gmail.com<br>🔗 [GitHub](https://github.com/dbtjgus6988) |
| FE | **이예진 (Yejin Lee)** | ComputerScience | - 프로젝트 기획<br>- 기술 스택 선정<br>- 와이어프레임 개발<br>- API 연결 및 기능 개발<br>- 전체 화면 UI 개발 | ✉️ clarecse02@gmail.com<br>🔗 [GitHub](https://github.com/lwjmcn) |
| BE | **한채린 (Chaelin Han)** | InformationSystem | "" | ✉️ chelin02@naver.com<br>🔗 [GitHub](https://github.com/han-chaelin) |
| BE | **김혜연 (Hyeyeon Kim)** | DataScience | - Flask 백엔드 초기 세팅<br>- MongoDB 연결 및 Render 배포<br>- 컬렉션 스키마 설계<br>- API 개발 (엔드포인트별 구현, OpenAI API 연동, JWT 인증)<br>- Background worker 개발<br>- Flaswagger 문서화 | ✉️ rbanbla@hanyang.ac.kr<br>🔗 [GitHub](https://github.com/rbanbla) |
| UI | **임선민 (Sunmin Lim)** | InformationSystem | - UI/UX 설계 및 디자인 보조<br>- 프론트엔드 UI 개발 보조<br>- 유저테스트 준비 보조 | ✉️ imsnmn24@gmail.com<br>🔗 [GitHub](https://github.com/Sunmin-Lim) |

---

## 설치 및 실행 방법 (Installation & Execution)
해당 프로젝트는 상단 링크에서 배포된 버전을 바로 확인하실 수 있습니다.
로컬 환경에서 실행하고자 할 경우, 아래의 절차를 따라 주세요.

### Backend
#### 1. Clone the repository
```bash
git clone https://github.com/techforimpact-archive/TFI_CAMPUS_HANYANG_25Spring_SalingtheMind.git
```
#### 2. Move to the back-end directory
```bash
cd backend-repo
```
#### 3. Install requirements (Make sure you are already using Python 3.8 or higher)
```bash
pip install -r requirements.txt
```
#### 4. Make `.env` file and fill it like below
```env
MONGO_URI=your MongoDB connection URI
DB_NAME=your MongoDB database name

JWT_SECRET_KEY=your JWT secret key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

OPENAI_API_KEY=your OpenAI API key (starts with sk-...)
```
#### 5. Run the app
```bash
python app.py
```
#### 6. Open `test.http` (Make sure you already installed REST Client extension)
- Click **"Send Request"** above the request line  
- Or manually send a request to:`http://localhost:5000`

### Frontend
#### 1. Clone the repository
```bash
git clone https://github.com/techforimpact-archive/TFI_CAMPUS_HANYANG_25Spring_SalingtheMind.git
```
#### 2. Move to the front-end directory
```bash
cd frontend-repo
```
#### 3. Install packages (Make sure you already installed Node.js and npm)
```bash
npm install
```
#### 4. Make `.env` file and fill it like below
```env
VITE_API_URL=your backend server url
VITE_GOOGLE_ANALYTICS_ID=your GA4 ID
```
#### 5. Run the app
```bash
npm run dev
```
#### 6. Go to the start page `http://localhost:3000` in your web browser

---

## 기술 스택
### 공통
*Notion,  Github*

### Frontend
*React,  Vite,  Typescript,  Zustand,  Axios,  CSSModules,  Vercel,  GitFlow   GoogleAnalytics4*
- `Vite + React` HMR 빠른 개발 속도  
- `Module CSS` 로 CSS 파일 분리  
- `Axios + REST API + Zustand` 로 API 요청 횟수 개선

### Backend
*Flask,  MongoDB,  JWT,  OpenAI GPT-4o API,  Render,  Flasgger*
- 프레임워크: `Flask` – 경량화된 웹 프레임워크로 RESTful API 설계
- 라우팅 & 인증: `JWT Auth` + Flask Blueprint – 사용자 인증 및 기능별 라우터 분리
- 데이터베이스: `MongoDB Atlas` – 유연한 비정형 데이터 저장 및 쿼리
- 문서화 도구: `Flasgger` – Swagger 기반 API 명세 자동화

---

## 프로젝트 구조
### Frontend
```plaintext
frontend-repo/
├── public/                    # 정적 파일들
│   ├── audio/
│   ├── font/
│   └── image/
├── src/
│   ├── components/            # 공통 UI 컴포넌트
│   │   ├── Appbar.tsx
│   │   ├── ...
│   │   ├── Toast.tsx
│   │   └── *.module.css
│   ├── lib/                   # API 요청 함수
│   │   ├── api/
│   │   ├── constants/
│   │   │   └── api.ts         # API 엔드포인트
│   │   ├── dto/               # API 요청/응답 구조
│   │   │   └── type/          # interface, enum
│   │   ├── axios.ts           # API 요청 기본 함수 (+ 액세스 토큰)
│   │   └── response_dto.ts    # API 응답 기본 구조
│   ├── pages/
│   │   ├── auth/              # 로그인/회원가입
│   │   ├── beach/
│   │   │   ├── received/      
│   │   │   │   ├── letter/    # 편지 수신, 답장 전송
│   │   │   │   └── response/  # 답장 수신
│   │   │   │   └── Beach.tsx  # 해변(편지/답장 수신)
│   │   │   ├── Main.tsx       # 메인
│   │   │   └── Setting.tsx    # 설정
│   │   ├── item/
│   │   │   ├── ItemDetail.tsx # 아이템 사용/해제
│   │   │   └── ItemList.tsx   # 아이템 목록
│   │   └── post/
│   │       ├── save/          # 저장된 편지 조회
│   │       ├── send/          # 편지 전송
│   │       └── PostOffice.tsx # 우체국
│   ├── store/                 # 전역 상태 관리
│   │   ├── audio.ts           # BGM 재생 상태
│   │   ├── auth.ts            # 로그인 상태
│   │   ├── item.ts            # 조회 API 결과
│   │   ├── ...                
│   │   └── toast.ts           # 토스트 UI 표시 상태
│   ├── App.tsx                # root
│   ├── global.css
│   ├── index.tsx
│   ├── layout.tsx            # 레이아웃, BGM 재생
│   └── route.tsx             # 페이지 라우팅 정의 (+ 보호 라우팅)
├── ...
├── index.html
├── package.json
├── tsconfig.json             # TypeScript 설정
├── vercel.json               # Vercel 배포 설정
├── vite.config.ts            # Vite 번들러 설정
└── vite-env.d.ts             # Vite 환경 타입 정의
```
### Backend
```plaintext
backend-repo
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
├── main.py                # Render 자동답장 스케줄러 파일
├── render.yaml            # Render 자동답장 설정 파일
├── requirements.txt       # 사용 라이브러리 목록
├── test.http              # HTTP 요청 테스트용 -REST Client 확장
└── README.md
```
<img width="376" alt="image" src="![제목 없는 다이어그램.drawio.svg](attachment:c01c0fc2-b1d8-4b66-a733-f6d9bca5ef78:제목_없는_다이어그램.drawio.svg)" />
**AI Service**
- GPT-4o API 기반 감정 맞춤 질문 생성
- 사용자 입력 응답 처리 및 텍스트 전처리
비즈니스 로직:
- 감정 기반 질문 제시 및 편지 처리
- GPT API를 활용한 자동 답장 생성
- 자동 응답 시스템:
    - Render의 Background Worker에서 자동응답 대상 편지를 탐색
    - GPT API 호출 후 응답 저장까지 주기적 처리

**Prompting**
- 정서적 라포 유도를 위한 GPT 기반 화법 설계
- 공감형 대화체로 감정 반응 유도
- GPT-4o를 활용한 문맥 이해 및 감정 표현 품질 향상

**Deployment**
- `Render` (Web Service와 Worker 인스턴스를 분리 배포)
  
---
## 주요 기능 Key Features & UI Overview
### 🏝 메인 화면
- 캐릭터 ‘온달’이 감정 표현과 지속 활동을 돕는 서포터 역할을 합니다.
- ‘집 가는 길’을 선택하면 편지를 작성하거나 개인 편지 보관함을 볼 수 있습니다.
- ‘해변 가는 길’을 선택하면 타인이 작성한 편지와 받은 답장을 볼 수 있습니다.
- 왼쪽 상단 조개 버튼을 누르면, 획득한 아이템으로 공간 커스터마이징할 수 있습니다.
<img width="250" alt="image" src="https://github.com/user-attachments/assets/874b0ccd-b867-4c38-8e29-59960a3d6b25" />

### 🌊 해변 화면 (편지 읽기/답장 공간)
- 바다에 떠있는 종이배를 선택하면 익명의 편지를 열람하고, 직접 답장을 보낼 수 있습니다.
- 편지가 담긴 유리병을 선택하면 자신이 보냈던 편지에 대한 답장을 열람할 수 있습니다.

### 💌 편지 및 답장 작성 화면
- 수신자 선택 → 감정 선택 → AI 기반 질문으로 편지 작성 유도 → 편지 작성
- 감정 기반 AI 질문으로 글쓰기를 시작하여, 전과정에서 내용 기반 AI 질문 도움을 받을 수 있습니다.
<img width="250" alt="image" src="https://github.com/user-attachments/assets/25cdac8e-1382-48a2-bcf8-365a2906688a" />
<img width="250" alt="image" src="![image.png](attachment:49cbce29-8113-4604-853a-0c9046c68051:image.png)" />

---

## 🧵 Troubleshooting
- 문제: BGM 자동재생 안 됨
    원인: 2018년 Chrome 브라우저 등은 사용자 피드백 없는 오디오 자동재생을 막도록 정책을 바꿈
    해결: `play()`에서 자동재생이 막히면 `catch`하여 `audioOn` 값을 `false`로 설정함. 이후, 사용자의 미디어 참여도 지수 기준점이 초과되면 `play()`에서 error가 발생하지 않고 올바르게 재생됨.
- 문제: 데이터 조회 화면에서 로딩이 자주 걸림
    원인: 컴포넌트가 마운트 될 때마다 API를 호출하여 로딩 시간이 길고 서버 부담이 큼
    해결: 자주 쓰이는 조회 API들의 결과를 `zustand`로 전역 상태 관리함. 로그인 시에 조회 API들을 미리 호출하여 로딩을 최소화함. POST API 요청으로 값이 바뀔 가능성이 있을 때, 새로고침 등의 이유로 상태가 초기화 되었을 때에만 API를 다시 호출하여 서버 부담을 줄임.
- 문제: 태블릿 및 PC에서 화면을 볼 수 없음
    원인: 모바일 브라우저 기준으로만 반응형이 되도록 개발하여 가로가 긴 화면에서는 아래가 잘림.
    해결: 전역에서 `pointer: fine`으로 PC 브라우저를 구분하여 `height`와 `aspect-ratio`로 좌우에 여백을 두어 모바일 환경에서와 같은 화면을 볼 수 있게 함. 태블릿과 휴대폰 가로모드 등 터치가 가능한 디바이스를 위해 `min-aspect-ratio: 2 / 3`과 `hover: none`으로 구분함.
- 문제: 배경에서 위쪽 또는 오른쪽에 얇은 흰 줄 여백이 생김
    원인: GPT로 생성한 배경 이미지의 끝부분의 여백
    해결: 배경에 적용되었던 이미지를 잘라서 수정함
- 문제: AI 도움말 사용률이 떨어짐
    원인: 팝업 말풍선을 여는 버튼이 앱바에 있어서 눈에 안 띔. 존재조차 몰랐던 사용자가 많음.
    해결: 편지 작성 화면에서 말풍선 버튼을 작성란 바로 위쪽으로 옮기고 대사에 타이핑 애니메이션을 줘서 시선을 끎.
- 문제: `bson` 모듈 에러
    원인: MongoDB 드라이버 누락
    해결: `pip install pymongo` 또는 `pip install bson`
- 문제: CORS 오류
    원인: 프론트/백엔드 도메인 불일치
    해결: Flask에서 `CORS(app, resources={r"/*": {"origins": "*"}})` 설정
- 문제: OpenAI API 오류
    원인: 키 누락 또는 요금제 문제
    해결: `.env` 파일에 `OPENAI_API_KEY=your-key` 등록
  
---

## 🔮 Future Work
- 악성 문구 및 유해 답장 필터링
- 받은 편지 카카오톡 알림 (편지 작성 리마인드 및 답장 도착 알림)
- 정서 회복 성장 여정 시각화 → 임팩트 지표 측정에 활용
- 위로 글귀 가챠
- 학교 및 복지기관 대상 온기 서비스 시연

---

## 🎓 Fellowship & Mentorship
- **Fellow**: 조현식 님 (온기 Onji) 🔗[Ongibox](https://ongibox.co.kr/)
- **Mentor**: 이정음 님 (카카오 Kakao) 🔗[GitHub](https://github.com/jeongum) 

---


