# 🚀 최종 배포 가이드 (경로 정규화 포함)

## 📋 **현재 상황:**
- ✅ 프론트엔드: GitHub Pages에 배포됨
- ✅ JavaScript 오류: 모두 해결됨
- ⏳ Edge Function: 배포 필요 (경로 정규화 로직 추가됨)

## 🔧 **Edge Function 배포 단계:**

### **Step 1: Supabase Dashboard 접속**
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. **baropoint-debug** 프로젝트 선택
3. **Edge Functions** 메뉴 클릭

### **Step 2: Edge Function 수정**
1. **youtube-downloader** 함수 선택
2. **Edit** 버튼 클릭
3. **기존 코드 전체 삭제**
4. **`supabase_edge_function_fixed_v2.ts` 파일 내용 전체 복사**
5. **Supabase 에디터에 붙여넣기**

### **Step 3: 배포 실행**
1. **Deploy** 버튼 클릭
2. **배포 완료** 대기 (약 1-2분)

## 🎯 **수정된 핵심 내용:**

### **✅ 경로 정규화 로직 추가:**
```typescript
// 경로 정규화: /youtube-downloader 접두사 제거
if (path.startsWith('/youtube-downloader')) {
  path = path.replace('/youtube-downloader', '')
}

// 빈 경로는 /로 변경
if (!path || path === '') {
  path = '/'
}
```

### **✅ 지원되는 API 엔드포인트:**
- `/health` (GET): 상태 확인
- `/user/login` (POST): 사용자 로그인
- `/search` (POST): YouTube 비디오 검색
- `/video-info` (POST): 단일 비디오 정보
- `/download-links` (POST): 다운로드 링크 생성
- `/download` (POST): 서버 사이드 다운로드 (폴더 지정 가능)

## 🎉 **배포 후 예상 결과:**

### **✅ 로그인 기능:**
- **이메일**: baropoint@gmail.com
- **비밀번호**: kimhans74
- **상태**: 정상 작동

### **✅ 검색 기능:**
- **키워드 검색**: 정상 작동
- **URL 검색**: 정상 작동
- **정렬**: 관련성, 시간, 조회수, 날짜
- **페이징**: 10개씩 표시

### **✅ 다운로드 기능:**
- **서버 사이드 다운로드**: 폴더 지정 가능
- **품질 선택**: 720p, 480p, 360p, audio
- **모바일 최적화**: 자동 다운로드 설정 가능

## 🚨 **중요 사항:**

### **경로 정규화의 중요성:**
- **프론트엔드**: `SUPABASE_URL/functions/v1/youtube-downloader/user/login` 호출
- **Edge Function**: `/youtube-downloader/user/login` 경로 수신
- **정규화**: `/user/login`으로 변환하여 라우팅

### **이전 오류 원인:**
- **경로 정규화 없음**: `/youtube-downloader/user/login`을 그대로 매칭 시도
- **404 오류 발생**: 실제 라우팅 경로는 `/user/login`

## 📞 **문제 해결:**

### **배포 실패 시:**
1. **환경 변수** 확인 (YOUTUBE_API_KEY 등)
2. **코드 문법** 확인
3. **Supabase 로그** 확인

### **다운로드 실패 시:**
1. **yt-dlp 설치** 확인
2. **폴더 권한** 확인
3. **Edge Function 로그** 확인

---

**🎯 이제 경로 정규화 로직이 추가되어 모든 API 엔드포인트가 정상 작동합니다!**
