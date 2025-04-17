# KGU Library

경기대학교 API 라이브러리는 경기대학교의 다양한 시스템에 프로그래밍 방식으로 접근할 수 있는 라이브러리입니다.

## 소개

이 프로젝트는 경기대학교 관련 다양한 서비스에 접근할 수 있는 Python API 라이브러리를 제공합니다. 현재는 도서관 좌석 예약 API가 구현되어 있으며, 추후 학생증, 학사 정보 등 다른 서비스에 대한 API도 추가될 예정입니다.

## 설치 방법

```bash
pip install kgu_library
```

## 의존성

### KISA_SEED_128_CBC

이 라이브러리는 한국인터넷진흥원(KISA)에서 제공하는 SEED 암호화 알고리즘을 사용합니다. userid 모듈을 사용하려면 먼저 KISA_SEED_128_CBC 라이브러리를 컴파일해야 합니다.

```bash
# kgu_library가 설치된 경로로 이동
cd site-packages/kgu_library/KISA_SEED_128_CBC/lib/seed_128_cbc

# 컴파일 스크립트 실행
bash compile.sh
```

Mac OS X 사용자는 다음과 같이 BIG_ENDIAN 매크로 재정의 경고가 발생할 수 있으나 무시해도 됩니다:

```
warning: 'BIG_ENDIAN' macro redefined
```

## 사용 가능한 모듈

현재 다음과 같은 API 모듈을 제공하고 있습니다:

### 1. 도서관 API (library)

경기대학교 도서관 예약 시스템 API 라이브러리입니다.

```python
from kgu_library.library import LibraryAPIWrapper, BookingStatus

# API 클라이언트 생성
api = LibraryAPIWrapper()

# 로그인
api.login("학번", "비밀번호")

# 좌석 예약
result = api.book_seat("A", "1")
if result["status"] == BookingStatus.SUCCESS:
    print("예약 성공!")
```

### 2. 사용자 정보 API (userid)

경기대학교 사용자 정보 시스템 API 라이브러리입니다.

```python
from kgu_library.userid import UserIDAPI

# API 클라이언트 생성
api = UserIDAPI()

# 로그인
api.login("학번", "비밀번호")

# QR 코드 정보 가져오기
qr_info = api.get_qr_code()
print(f"QR 코드 정보: {qr_info}")

# 사용자 ID로 사용자 검색
results = api.search_user_by_id("대상ID")
for user in results:
    print(f"이름: {user['sugang_student_name']}, ID: {user['sugang_student_id']}")

# 친구 요청 보내기
api.send_friend_request("사용자ID")

# 친구 목록 조회
friends = api.get_friend_list()
for friend in friends:
    print(f"친구: {friend['friend_name']}")
```

## 개발 환경 설정

개발에 참여하시려면 다음 단계를 따라주세요:

1. 저장소 클론:

   ```bash
   git clone https://github.com/kgu-utils/kgu_library.git
   cd kgu_library
   ```

2. 가상 환경 설정:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 개발 의존성 설치:
   ```bash
   pip install -e .
   ```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 기여하기

이슈 제보, 기능 요청, 풀 리퀘스트 등 모든 기여를 환영합니다. 기여하기 전에 이슈를 먼저 개설하여 논의하는 것을 권장합니다.

## 프로젝트 구조

```
kgu_library/
├── library/               # 도서관 API 모듈
│   ├── api.py             # 도서관 API 래퍼
│   ├── http_client.py     # HTTP 클라이언트
│   ├── enums.py           # 열거형 (예: 예약 상태)
│   └── exceptions.py      # 예외 클래스
├── attendance/            # 전자출결 API 모듈
│   ├── api.py             # 전자출결 API 래퍼
│   ├── http_client.py     # HTTP 클라이언트
│   ├── enums.py           # 열거형 (예: 출석 상태)
│   └── exceptions.py      # 예외 클래스
├── userid/                # 사용자 정보 API 모듈
│   ├── api.py             # 사용자 정보 API 래퍼
│   ├── http_client.py     # HTTP 클라이언트
│   ├── enums.py           # 열거형 (사용자 상태 등)
│   └── exceptions.py      # 예외 클래스
├── core/                  # 핵심 유틸리티 모듈
│   └── crypto/            # 암호화 관련 유틸리티
└── __init__.py            # 패키지 초기화
```

## 문의

문의사항이 있으시면 다음 연락처로 문의하세요:

- 이메일: rmagur1203@kyonggi.ac.kr
