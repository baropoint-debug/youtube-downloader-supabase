# 🚀 외부 접속 가능한 유튜브 다운로더 배포 가이드

## 📋 배포 전 준비사항

### 1. **Supabase 데이터베이스 설정**
1. Supabase 대시보드 → **SQL Editor** 클릭
2. **New Query** 클릭
3. `supabase_production_schema.sql` 파일의 내용을 복사해서 붙여넣기
4. **Run** 버튼 클릭하여 실행

### 2. **환경 변수 설정**
배포 플랫폼에서 다음 환경 변수를 설정하세요:

```bash
# Supabase 설정
SUPABASE_URL=https://qhrfefcthrogwdwpxkby.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4MTg1ODUsImV4cCI6MjA3NTM5NDU4NX0.Do9gajWdwgP8PFSlajAUhZHb024nfNZNnx1IJz9yR5k
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTgxODU4NSwiZXhwIjoyMDc1Mzk0NTg1fQ.wBg6ziXqViZHlXXfOryW12YbOpe54_cj5rD-4C1p7P8

# YouTube API 설정
YOUTUBE_API_KEY=AIzaSyA1v9qsqY3TLYrsjJngs6MHDBwnFvIURuA

# Flask 설정
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key-here
```

## 🌐 배포 옵션

### **옵션 1: Vercel 배포 (권장)**

#### 1. **Vercel CLI 설치**
```bash
npm i -g vercel
```

#### 2. **프로젝트 배포**
```bash
# Vercel 로그인
vercel login

# 프로젝트 배포
vercel --prod

# 환경 변수 설정
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add YOUTUBE_API_KEY
vercel env add FLASK_SECRET_KEY
```

#### 3. **도메인 설정**
- Vercel 대시보드에서 커스텀 도메인 설정 가능

---

### **옵션 2: Railway 배포**

#### 1. **Railway CLI 설치**
```bash
npm install -g @railway/cli
```

#### 2. **프로젝트 배포**
```bash
# Railway 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up

# 환경 변수 설정
railway variables set SUPABASE_URL=https://qhrfefcthrogwdwpxkby.supabase.co
railway variables set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
railway variables set SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
railway variables set YOUTUBE_API_KEY=AIzaSyA1v9qsqY3TLYrsjJngs6MHDBwnFvIURuA
railway variables set FLASK_SECRET_KEY=your-secret-key-here
```

---

### **옵션 3: Heroku 배포**

#### 1. **Heroku CLI 설치**
```bash
# Windows
winget install Heroku.HerokuCLI

# 또는 다운로드: https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. **프로젝트 배포**
```bash
# Heroku 로그인
heroku login

# 앱 생성
heroku create your-youtube-downloader

# 환경 변수 설정
heroku config:set SUPABASE_URL=https://qhrfefcthrogwdwpxkby.supabase.co
heroku config:set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
heroku config:set SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
heroku config:set YOUTUBE_API_KEY=AIzaSyA1v9qsqY3TLYrsjJngs6MHDBwnFvIURuA
heroku config:set FLASK_SECRET_KEY=your-secret-key-here

# 배포
git push heroku main
```

---

### **옵션 4: Docker 배포**

#### 1. **Docker 이미지 빌드**
```bash
docker build -t youtube-downloader .
```

#### 2. **Docker 컨테이너 실행**
```bash
docker run -d \
  -p 5001:5001 \
  -e SUPABASE_URL=https://qhrfefcthrogwdwpxkby.supabase.co \
  -e SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... \
  -e SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... \
  -e YOUTUBE_API_KEY=AIzaSyA1v9qsqY3TLYrsjJngs6MHDBwnFvIURuA \
  -e FLASK_SECRET_KEY=your-secret-key-here \
  --name youtube-downloader \
  youtube-downloader
```

---

## 🔧 배포 후 설정

### 1. **도메인 설정**
- **Vercel**: 대시보드에서 커스텀 도메인 추가
- **Railway**: 자동으로 제공되는 도메인 사용
- **Heroku**: `your-app-name.herokuapp.com` 형태로 자동 생성

### 2. **SSL 인증서**
- 모든 플랫폼에서 자동으로 HTTPS 제공
- SSL 인증서 자동 갱신

### 3. **모니터링 설정**
- **Vercel**: Analytics 대시보드
- **Railway**: Metrics 탭
- **Heroku**: Heroku Metrics

## 🧪 배포 후 테스트

### 1. **헬스체크**
```bash
curl https://your-domain.com/api/health
```

### 2. **기능 테스트**
1. 웹사이트 접속
2. 이메일로 회원가입/로그인
3. 유튜브 비디오 검색
4. 비디오 다운로드
5. 히스토리 및 즐겨찾기 기능

## 🚨 문제 해결

### **일반적인 문제들**

#### 1. **Supabase 연결 실패**
- 환경 변수 확인
- Supabase 프로젝트 상태 확인
- 네트워크 연결 확인

#### 2. **YouTube API 오류**
- API 키 유효성 확인
- 할당량 초과 여부 확인

#### 3. **다운로드 실패**
- 서버 디스크 공간 확인
- 파일 권한 확인

#### 4. **CORS 오류**
- Flask-CORS 설정 확인
- 도메인 설정 확인

## 📊 성능 최적화

### 1. **캐싱 설정**
- Redis를 통한 세션 캐싱
- CDN을 통한 정적 파일 캐싱

### 2. **데이터베이스 최적화**
- 인덱스 최적화
- 쿼리 성능 모니터링

### 3. **서버 리소스**
- CPU/메모리 사용량 모니터링
- 자동 스케일링 설정

## 🔒 보안 설정

### 1. **API 보안**
- Rate Limiting 적용
- CORS 정책 설정
- 입력 데이터 검증

### 2. **데이터 보안**
- RLS (Row Level Security) 활성화
- 사용자별 데이터 격리
- 민감한 정보 암호화

## 📈 모니터링 및 로깅

### 1. **로그 설정**
- 애플리케이션 로그
- 에러 로그
- 성능 로그

### 2. **메트릭 수집**
- 사용자 활동 추적
- 다운로드 통계
- 시스템 성능 지표

## 🎉 완료!

배포가 완료되면 전 세계 어디서든 접속 가능한 유튜브 다운로더 서비스가 됩니다!

**주요 기능:**
- ✅ 사용자 관리 (회원가입/로그인)
- ✅ 유튜브 비디오 검색
- ✅ 비디오 다운로드
- ✅ 다운로드 히스토리
- ✅ 즐겨찾기 기능
- ✅ 반응형 웹 디자인
- ✅ 실시간 상태 업데이트
