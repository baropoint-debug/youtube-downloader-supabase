# YouTube Data API v3 설정 가이드

## 1. Google Cloud Console에서 API 키 발급

### 1.1 Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. Google 계정으로 로그인

### 1.2 프로젝트 생성/선택
1. 상단의 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 클릭하여 새 프로젝트 생성
   - 프로젝트 이름: `youtube-downloader` (또는 원하는 이름)
   - 프로젝트 ID: 자동 생성됨
3. "만들기" 클릭

### 1.3 YouTube Data API v3 활성화
1. 왼쪽 메뉴에서 "API 및 서비스" → "라이브러리" 클릭
2. 검색창에 "YouTube Data API v3" 입력
3. "YouTube Data API v3" 클릭
4. "사용" 버튼 클릭

### 1.4 API 키 생성
1. 왼쪽 메뉴에서 "API 및 서비스" → "사용자 인증 정보" 클릭
2. "사용자 인증 정보 만들기" → "API 키" 클릭
3. 생성된 API 키를 복사하여 안전한 곳에 보관

## 2. API 키 설정

### 2.1 app.py 파일 수정
1. `app.py` 파일을 텍스트 에디터로 열기
2. 다음 줄을 찾기:
   ```python
   YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"
   ```
3. `YOUR_API_KEY_HERE` 부분을 실제 API 키로 교체:
   ```python
   YOUTUBE_API_KEY = "AIzaSyC...your_actual_api_key_here...xyz"
   ```

### 2.2 API 키 보안 주의사항
- API 키를 GitHub 등에 공개하지 마세요
- `.env` 파일을 사용하여 환경변수로 관리하는 것을 권장합니다

## 3. API 할당량 및 제한

### 3.1 기본 할당량
- **일일 할당량**: 10,000 units
- **검색 요청**: 100 units
- **비디오 정보 요청**: 1 unit

### 3.2 할당량 확인 방법
1. Google Cloud Console → "API 및 서비스" → "대시보드"
2. "YouTube Data API v3" 클릭
3. "할당량" 탭에서 사용량 확인

### 3.3 할당량 증가 요청
- 할당량이 부족한 경우 Google에 증가 요청 가능
- 비즈니스 계정의 경우 더 높은 할당량 제공

## 4. 테스트 및 확인

### 4.1 앱 실행
```bash
python app.py
```

### 4.2 API 키 설정 확인
앱 실행 시 다음 메시지가 나타나면 정상:
```
Flask 앱이 시작되었습니다.
다운로드 폴더: C:\Faceon\video\down
웹 브라우저에서 http://localhost:5000 으로 접속하세요.
```

### 4.3 API 키 미설정 시
다음 경고 메시지가 나타남:
```
⚠️  경고: YouTube Data API 키가 설정되지 않았습니다.
   app.py 파일에서 YOUTUBE_API_KEY 변수를 실제 API 키로 교체하세요.
   API 키 없이도 mock 데이터로 검색은 가능하지만, 실제 YouTube 검색은 작동하지 않습니다.
```

## 5. 문제 해결

### 5.1 API 키 오류
- **오류**: `API key not valid`
- **해결**: API 키가 올바르게 설정되었는지 확인

### 5.2 할당량 초과
- **오류**: `Quota exceeded`
- **해결**: 다음날까지 대기하거나 할당량 증가 요청

### 5.3 API 비활성화
- **오류**: `API not enabled`
- **해결**: Google Cloud Console에서 YouTube Data API v3 활성화 확인

## 6. 환경변수 사용 (권장)

### 6.1 .env 파일 생성
프로젝트 루트에 `.env` 파일 생성:
```
YOUTUBE_API_KEY=your_actual_api_key_here
```

### 6.2 python-dotenv 설치
```bash
pip install python-dotenv
```

### 6.3 app.py 수정
```python
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")
```

## 7. 추가 기능

### 7.1 검색 필터링
- `videoDuration`: 짧은/중간/긴 비디오 필터링
- `videoDefinition`: HD/SD 비디오 필터링
- `videoEmbeddable`: 임베드 가능한 비디오만

### 7.2 정렬 옵션
- `relevance`: 관련성 순
- `date`: 업로드 날짜 순
- `viewCount`: 조회수 순
- `rating`: 평점 순

## 8. 비용 정보

- **YouTube Data API v3**: 무료 (할당량 내에서)
- **할당량 초과 시**: Google Cloud Platform 요금 정책에 따라 과금
- **일반적인 사용**: 무료 할당량으로 충분

## 9. 지원 및 도움말

- [YouTube Data API v3 공식 문서](https://developers.google.com/youtube/v3)
- [Google Cloud Console 도움말](https://cloud.google.com/docs)
- [API 할당량 및 가격](https://developers.google.com/youtube/v3/getting-started#quota)



