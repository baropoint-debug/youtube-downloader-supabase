# 🚀 Supabase Edge Function 배포 가이드

## 📋 **배포할 파일:**
**`supabase_edge_function_fixed_v2.ts`** 파일의 전체 내용

## 🔧 **배포 단계:**

### **Step 1: Supabase 대시보드 접속**
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. **baropoint-debug** 프로젝트 선택
3. **Edge Functions** 메뉴 클릭

### **Step 2: Edge Function 수정**
1. **youtube-downloader** 함수 선택
2. **Edit** 버튼 클릭
3. **기존 코드 전체 삭제**
4. **`supabase_edge_function_fixed_v2.ts` 파일 내용 전체 복사**
5. **Supabase 에디터에 붙여넣기**

### **Step 3: 환경 변수 확인**
1. **Settings** → **Edge Functions** → **Secrets**
2. 다음 변수들이 설정되어 있는지 확인:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_DB_URL`
   - `YOUTUBE_API_KEY`

### **Step 4: 배포 실행**
1. **Deploy** 버튼 클릭
2. **배포 완료** 대기 (약 1-2분)

## 🎯 **새로운 기능:**

### **✅ 서버 사이드 다운로드:**
- **폴더 지정**: 사용자가 원하는 경로에 다운로드
- **yt-dlp 사용**: 실제 YouTube 다운로드
- **품질 선택**: 720p, 480p, 360p, audio
- **진행 상황**: 서버에서 다운로드 완료 후 알림

### **✅ 프론트엔드 개선:**
- **다운로드 경로 입력**: 설정에서 폴더 경로 지정
- **서버 API 호출**: `/download` 엔드포인트 사용
- **완료 알림**: 다운로드 완료 시 저장 위치 표시

## 💡 **사용 방법:**

### **1. 설정에서 다운로드 경로 지정:**
```
Windows: C:\Downloads\YouTube
Mac: /Users/username/Downloads/YouTube
Linux: /home/username/Downloads/YouTube
```

### **2. 다운로드 실행:**
1. **비디오 검색** → **다운로드** 클릭
2. **품질 선택** (720p 권장)
3. **서버에서 다운로드** → **지정한 폴더에 저장**
4. **완료 알림** 표시

## ⚠️ **주의사항:**

### **Edge Function 제한:**
- **실행 시간**: 최대 300초 (5분)
- **메모리**: 최대 512MB
- **파일 크기**: 큰 비디오는 시간 초과 가능

### **yt-dlp 설치:**
- **Supabase Edge Function**에 yt-dlp가 설치되어 있는지 확인 필요
- **설치되지 않은 경우**: Supabase 지원팀에 문의

## 🎉 **완료 후 테스트:**

### **1. 로그인 테스트:**
- **이메일**: baropoint@gmail.com
- **비밀번호**: kimhans74

### **2. 검색 테스트:**
- **키워드 검색** 정상 작동
- **URL 검색** 정상 작동

### **3. 다운로드 테스트:**
- **품질 선택** 정상 작동
- **서버 다운로드** 정상 작동
- **폴더 저장** 정상 작동

## 📞 **문제 해결:**

### **배포 실패 시:**
1. **환경 변수** 확인
2. **코드 문법** 확인
3. **Supabase 로그** 확인

### **다운로드 실패 시:**
1. **yt-dlp 설치** 확인
2. **폴더 권한** 확인
3. **Edge Function 로그** 확인

---

**🎯 이제 로컬 Flask 앱과 동일한 기능을 웹에서 사용할 수 있습니다!**
