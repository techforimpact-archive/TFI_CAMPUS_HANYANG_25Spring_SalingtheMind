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

---

## ✍️ 주요 기능 (Key Features)
- 감정 기반 편지 작성을 통한 자기 표현
- GPT-4o를 활용한 감정/내용 기반 질문 및 제안 제공
- 개인보관함/익명사용자/온기우편함 대상 편지 송수신 교류
- 메인 화면 꾸미기용 포인트 기반 보상 시스템

---
## ⚙️ Technical Implementation

### 🧩 시스템 아키텍처

#### Frontend
- 사용자 인터페이스: `mobile web + module css`
- 상태 관리 & 라우팅: `Zustand + React Router`
- API 통신: `Axios + REST API`

#### Backend
- 인증 및 라우팅: `JWT Auth + Flask Routes`
- 서비스 로직: 감정 분석 및 질문 생성
- 데이터베이스: `MongoDB`

#### AI Service
- GPT-4o API 기반 감정 맞춤 질문 생성
- 사용자 입력 응답 처리 및 텍스트 전처리

### 🤖 Prompting
- 정서적 라포 유도를 위한 GPT 기반 화법 설계
- 공감형 대화체로 감정 반응 유도
- GPT-4o를 활용한 문맥 이해 및 감정 표현 품질 향상

### 🚀 Deployment
- **Frontend**: `Vercel` (자동 배포 및 CDN)
- **Backend**: `Render` (API 서버 및 DB 호스팅)

---

## 🛠 Development Environment

| Category   | Stack / Tool |
|------------|--------------|
| **Frontend** | React + Zustand + Module CSS |
| **Backend** | Flask + JWT + MongoDB |
| **AI Service** | OpenAI GPT-4o API |
| **Deployment** | Vercel (Frontend), Render (Backend) |
| **Others** | Axios, REST API, Notion (Issue Mgmt), GitHub (Version Control) |

---

## 🧑‍🤝‍🧑 Team Members

| Name | Affiliation | Role | Responsibility | Contact |
|------|------|------|----------------|---------|
| **유서현 (Seohyeon Yoo)** | DataScience | 리더 (PM) | "" | ✉️ dbtjgus6988@gmail.com<br>🔗 [GitHub](https://github.com/dbtjgus6988) |
| **이예진 (Yejin Lee)** | ComputerScience | 프론트엔드 개발자 | "" | ✉️ clarecse02@gmail.com<br>🔗 [GitHub](https://github.com/lwjmcn) |
| **한채연 (Chaelin Han)** | InformationSystem | 백엔드 개발자 | "" | ✉️ chelin02@naver.com<br>🔗 [GitHub](https://github.com/han-chaelin) |
| **김혜연 (Hyeyeon Kim)** | DataScience | 백엔드 개발자 | "" | ✉️ rbanbla@hanyang.ac.kr<br>🔗 [GitHub](https://github.com/rbanbla) |
| **임선민 (Sunmin Lim)** | InformationSystem | UI 디자이너 | "" | ✉️ imsnmn24@gmail.com<br>🔗 [GitHub](https://github.com/Sunmin-Lim) |

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
