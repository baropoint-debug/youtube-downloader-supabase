# 🚨 긴급 배포 가이드

## 📋 **현재 상황:**
- ✅ 프론트엔드: GitHub Pages에 배포됨
- ✅ Edge Function 코드: 준비 완료 (`supabase_edge_function_fixed_v2.ts`)
- ❌ Edge Function 배포: **아직 배포되지 않음**
- ❌ 오류: `POST /download 500 (Internal Server Error)`

## 🚀 **즉시 해야 할 일:**

### **Step 1: Supabase Dashboard 접속**
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. **baropoint-debug** 프로젝트 선택
3. **Edge Functions** 메뉴 클릭

### **Step 2: Edge Function 배포**
1. **youtube-downloader** 함수 선택
2. **Edit** 버튼 클릭
3. **기존 코드 전체 삭제**
4. **`supabase_edge_function_fixed_v2.ts` 파일 열기**
5. **전체 내용 복사 (Ctrl+A, Ctrl+C)**
6. **Supabase 에디터에 붙여넣기 (Ctrl+V)**
7. **Deploy** 버튼 클릭
8. **배포 완료 대기 (약 1-2분)**

### **Step 3: 환경 변수 확인**
1. **Settings** → **Edge Functions** → **Secrets**
2. 다음 변수 확인:
   - `SUPABASE_URL` ✅
   - `SUPABASE_ANON_KEY` ✅
   - `YOUTUBE_API_KEY` ✅

### **Step 4: 배포 확인**
1. 브라우저에서 사이트 새로고침 (Ctrl+F5)
2. 로그인: baropoint@gmail.com / kimhans74
3. 비디오 검색
4. 다운로드 클릭
5. 정상 작동 확인

## 🎯 **배포할 코드 위치:**
- **파일**: `c:\Faceon\video\supabase_edge_function_fixed_v2.ts`
- **줄 수**: 461 lines
- **주요 기능**:
  - ✅ 경로 정규화 로직
  - ✅ 사용자 로그인
  - ✅ YouTube 검색
  - ✅ 서버 사이드 다운로드
  - ✅ 폴더 지정 다운로드

## ⚠️ **주의사항:**

### **배포 전 확인:**
1. **파일**: `supabase_edge_function_fixed_v2.ts` (461줄)
2. **경로 정규화**: 코드 28-36줄에 있어야 함
3. **다운로드 엔드포인트**: 코드 336-406줄에 있어야 함

### **배포 후 확인:**
1. **로그인**: 정상 작동
2. **검색**: YouTube API 정상 작동
3. **다운로드**: 서버 다운로드 정상 작동
4. **폴더 저장**: 지정된 경로에 저장

## 🎉 **배포 완료 후 예상 결과:**

### **✅ 모든 기능 정상 작동:**
- **로그인**: baropoint@gmail.com
- **검색**: 키워드 & URL
- **다운로드**: 서버 사이드 (폴더 지정)
- **품질**: 720p, 480p, 360p, audio
- **경로**: C:\Downloads\YouTube (설정에서 지정)

---

**🚨 지금 바로 Supabase Dashboard에서 Edge Function을 배포해주세요!**
