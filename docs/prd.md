# 1. 프로젝트 개요

- 프로젝트명: AI 에이전트 기반 수강신청 플랫폼 (Course Registration with AI Agent)
- 목적: 구글 로그인을 기반으로, 학생은 AI 에이전트와 대화하며 수강 신청을 진행하고, 관리자는 전통적인 대시보드 UI를 통해 시스템을 관리하는 하이브리드 웹 서비스 구축.
- 핵심 가치: 사용자 편의성(Agentic UI)과 관리 정확성(Traditional Admin UI)의 조화.

# 2. 시스템 아키텍처 및 활용 기술

## 2.1 기술 스택 (Tech Stack)

|분류|기술|비고|
|Frontend|React (Vite), Tailwind CSS, React Query|빠른 UI 및 상태 관리|
|Backend|FastAPI, FastMCP (Python), Gemini API|API 및 MCP 에이전트 서버|
|Platform|Firebase (Auth, Hosting, Functions)|서버리스 배포 환경|
|Database|Cloud Firestore|NoSQL 기반 실시간 데이터베이스|
|AI 모델|openai|에이전트 추론 엔진|

## 2.2 하이브리드 인터페이스 구조

- 학생 (Agentic UI): 채팅창을 통한 자연어 인터렉션 (React ↔ Agent Server ↔ MCP ↔ Firestore)
- 관리자 (Traditional UI): 표와 폼을 통한 정밀 관리 (React ↔ FastAPI Admin API ↔ Firestore)

# 3. 기능 요구사항

## 3.1 인증 및 권한 (Auth & RBAC)

- Google OAuth: Firebase Authentication을 통한 구글 소셜 로그인.
- 자동 학생 ID 매핑: 구글 로그인 시 발급되는 고유 UID를 학생 ID로 사용하여, 사용자가 별도로 ID를 입력하거나 기억할 필요 없음.
- Role 기반 권한:
- student (기본): 로그인 시 자동 부여. 수강 조회 및 신청 가능.
- admin: 관리자 화면 접근 및 학생 권한 변경 가능.
- 권한 제어: API 요청 시 Firebase ID Token을 검증하여 역할(Role)에 따른 접근 제한.

## 3.2 학생용 서비스: AI 에이전트

- 자연어 수강신청: "이번 주 파이썬 강의 신청해줘" 등 자연어 명령어 처리.
- MCP 도구(Tools) 구성:
- list_courses: 신청 가능 강의 및 잔여석 조회.
- enroll_course: 수강 신청 (정원 확인 및 중복 방지 로직 포함).
- get_my_status: 본인의 수강 신청 현황 확인.
- 음성 인터페이스 (Voice Interface):
- STT (Speech-to-Text): 브라우저 내장 Web Speech API를 활용하여 음성 입력을 텍스트로 변환.
- TTS (Text-to-Speech): 에이전트의 응답을 브라우저 내장 음성 합성 기능을 통해 출력.
- 동작 방식:
- 채팅창 옆 [마이크] 버튼 클릭 시 음성 인식 활성화.
- 에이전트 답변 완료 시 자동으로 읽어주기 기능(옵션) 제공.

## 3.3 관리자용 서비스: 대시보드

- 강의 관리: 강의 생성(C), 조회(R), 수정(U), 삭제(D) 기능을 전통적 폼 형태로 제공.
- 유저 관리: 가입된 유저 목록 확인 및 특정 유저에게 관리자 권한 부여.
- 통계 확인: 강의별 수강 인원 실시간 모니터링.

# 4. 상세 폴더 구조

course-registration/ # 전체 프로젝트 루트 (Monorepo)
├── docs/ # 프로젝트 문서 (prd.md, diagrams)
├── functions/ # Firebase Functions (Python) - Backend 역할
│ ├── main.py # FastAPI + MCP 도구 + Agent (통합 진입점)
│ └── requirements.txt
├── frontend/ # Firebase Hosting (React)
│ ├── src/
│ │ ├── pages/ # Home, Student(Chat), Admin(Dashboard)
│ │ ├── hooks/ # 커스텀 훅 (useAuth, useCourses 등)
│ │ ├── components/ # UI 요소 (ChatWindow, CourseTable 등)
│ │ └── firebase.js # SDK 설정
│ └── package.json
├── firebase.json # 통합 배포 설정 파일
└── README.md

# 5. 데이터베이스 설계 (Firestore)

## 5.1 users (Collection)

- uid (PK): Firebase Auth UID
- email: 사용자 이메일
- role: "student" | "admin"
- name: 사용자 이름

## 5.2 courses (Collection)

- id (PK): 자동 생성 ID
- title: 강의명
- instructor: 강사명
- max_students: 정원
- current_count: 현재 신청 인원

## 5.3 enrollments (Collection)

- id (PK): studentId_courseId 형식으로 중복 신청 원천 차단
- student_id: 유저 UID
- course_id: 강의 ID
- timestamp: 신청 일시

# 6. 비기능적 요구사항

- 보안: 관리자 전용 API 호출 시 서버 사이드 권한 검증 필수.
- 성능: 에이전트 응답 지연 시 사용자에게 'Thinking...' 상태 피드백 제공.
- 확장성: MCP 도구를 추가하여 향후 출석 관리, 성적 조회 등으로 확장 가능하도록 설계.
