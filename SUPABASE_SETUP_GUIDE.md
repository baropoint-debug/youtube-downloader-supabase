# Supabase 연동 유튜브 다운로더 설정 가이드

## 개요
기존 유튜브 다운로드 프로그램을 Supabase 데이터베이스를 활용한 웹 애플리케이션으로 업그레이드했습니다.

## 주요 기능
- ✅ 사용자 관리 (등록/로그인)
- ✅ 다운로드 히스토리 추적
- ✅ 즐겨찾기 기능
- ✅ 실시간 다운로드 상태 관리
- ✅ 기존 YouTube 검색 및 다운로드 기능 유지

## 설정 단계

### 1. Supabase 프로젝트 생성
1. [Supabase](https://supabase.com)에 접속하여 새 프로젝트 생성
2. 프로젝트 URL과 API 키 확인

### 2. 데이터베이스 스키마 설정
1. Supabase 대시보드에서 SQL Editor 열기
2. `supabase_schema.sql` 파일의 내용을 복사하여 실행
3. 다음 테이블들이 생성됩니다:
   - `users`: 사용자 정보
   - `download_jobs`: 다운로드 작업
   - `download_history`: 다운로드 히스토리
   - `user_favorites`: 사용자 즐겨찾기
   - `user_playlists`: 사용자 플레이리스트
   - `playlist_videos`: 플레이리스트 비디오

### 3. 환경 변수 설정
`config.py` 파일에서 Supabase 설정을 업데이트하세요:

```python
# Supabase 설정
SUPABASE_URL = "your-supabase-url-here"
SUPABASE_ANON_KEY = "your-supabase-anon-key-here"
SUPABASE_SERVICE_ROLE_KEY = "your-supabase-service-role-key-here"
```

### 4. 패키지 설치
```bash
pip install -r requirements.txt
```

### 5. 애플리케이션 실행
```bash
python app.py
```

## API 엔드포인트

### 사용자 관리
- `POST /api/user/register` - 사용자 등록
- `POST /api/user/login` - 사용자 로그인

### 다운로드 관리
- `GET /api/user/{user_id}/jobs` - 사용자 다운로드 작업 목록
- `GET /api/user/{user_id}/history` - 사용자 다운로드 히스토리
- `GET /api/job/{job_id}` - 특정 작업 상태 조회

### 즐겨찾기 관리
- `GET /api/user/{user_id}/favorites` - 즐겨찾기 목록
- `POST /api/user/{user_id}/favorites` - 즐겨찾기 추가
- `DELETE /api/user/{user_id}/favorites` - 즐겨찾기 제거

### 시스템 상태
- `GET /api/health` - 시스템 상태 확인

## 사용법

### 1. 사용자 등록/로그인
- 웹 페이지 상단의 이메일 입력 필드에 이메일 입력
- 로그인 버튼 클릭
- 기존 사용자가 아니면 자동으로 새 계정 생성

### 2. 비디오 다운로드
- 기존과 동일하게 URL 입력 또는 검색어로 비디오 찾기
- 로그인된 상태에서 다운로드하면 히스토리에 자동 저장

### 3. 히스토리 확인
- 로그인 후 "히스토리" 버튼 클릭
- 과거 다운로드한 비디오 목록 확인

### 4. 즐겨찾기 관리
- 로그인 후 "즐겨찾기" 버튼 클릭
- 즐겨찾기 추가/제거 가능

## 데이터베이스 구조

### users 테이블
```sql
- id: UUID (Primary Key)
- email: TEXT (Unique)
- name: TEXT
- avatar_url: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### download_jobs 테이블
```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- video_url: TEXT
- video_title: TEXT
- video_thumbnail: TEXT
- channel_name: TEXT
- video_duration: TEXT
- video_description: TEXT
- status: TEXT (pending, downloading, completed, failed, cancelled)
- download_path: TEXT
- file_size: BIGINT
- file_format: TEXT
- progress: INTEGER
- error_message: TEXT
- created_at: TIMESTAMP
- started_at: TIMESTAMP
- completed_at: TIMESTAMP
```

### download_history 테이블
```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- job_id: UUID (Foreign Key)
- action: TEXT
- details: JSONB
- created_at: TIMESTAMP
```

## 보안 설정

### Row Level Security (RLS)
- 모든 테이블에 RLS가 활성화되어 있습니다
- 사용자는 자신의 데이터만 접근 가능
- 공개 플레이리스트는 모든 사용자가 볼 수 있음

### 인증
- 현재는 간단한 이메일 기반 인증
- 향후 Supabase Auth를 통한 강화된 인증 시스템으로 업그레이드 가능

## 문제 해결

### Supabase 연결 실패
1. `config.py`에서 URL과 API 키 확인
2. Supabase 프로젝트가 활성 상태인지 확인
3. 네트워크 연결 상태 확인

### 데이터베이스 오류
1. `supabase_schema.sql`이 올바르게 실행되었는지 확인
2. 테이블 권한 설정 확인
3. RLS 정책이 올바르게 설정되었는지 확인

### 다운로드 실패
1. YouTube API 키 설정 확인
2. 다운로드 폴더 권한 확인
3. yt-dlp 업데이트 확인

## 향후 개선 사항

1. **실시간 알림**: WebSocket을 통한 실시간 다운로드 진행률
2. **클라우드 스토리지**: Supabase Storage 연동
3. **공유 기능**: 플레이리스트 공유
4. **모바일 최적화**: 반응형 디자인 개선
5. **인증 강화**: OAuth, 2FA 등

## 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 메시지 확인
2. `/api/health` 엔드포인트로 시스템 상태 확인
3. Supabase 대시보드에서 데이터베이스 상태 확인

