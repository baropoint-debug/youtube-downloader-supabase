# 🔧 문제 해결 가이드

## 🚨 **발견된 문제들**

### **1. Edge Function 이름 확인 필요**
- **문제**: 코드에서 `youtube-downloader`라는 함수 이름을 사용하지만, 실제 배포된 함수 이름이 다를 수 있음
- **해결**: Supabase 대시보드에서 **실제 배포된 함수 이름 확인** 필요

#### **✅ Supabase 대시보드에서 확인하는 방법:**
1. **Supabase 대시보드** → **Edge Functions**
2. **배포된 함수 목록 확인**
3. **함수 이름이 `youtube-downloader`인지 확인**

#### **❌ 함수가 없다면:**
1. **`SUPABASE_EDGE_FUNCTION_SETUP.md`** 파일 참고
2. **Edge Function 새로 생성 및 배포**
3. **환경 변수 설정** (`YOUTUBE_API_KEY` 등)

---

### **2. API 엔드포인트 정리**

#### **✅ 현재 사용 중인 엔드포인트:**
| 엔드포인트 | 메서드 | 설명 |
|---------|-------|------|
| `/user/login` | POST | 사용자 로그인 |
| `/search` | POST | YouTube 검색 |
| `/download-links` | POST | 다운로드 링크 생성 |

#### **❌ 제거된 엔드포인트:**
- ~~`/api/download`~~ - 더 이상 사용하지 않음 (클라이언트 사이드 다운로드로 변경)

---

### **3. Edge Function 배포 체크리스트**

#### **필수 확인 사항:**
- [ ] **함수 이름**: `youtube-downloader` (또는 다른 이름)
- [ ] **환경 변수 설정**:
  - `YOUTUBE_API_KEY`: YouTube Data API v3 키
  - `SUPABASE_URL`: 자동 설정됨
  - `SUPABASE_ANON_KEY`: 자동 설정됨
  - `SUPABASE_SERVICE_ROLE_KEY`: 자동 설정됨
  - `SUPABASE_DB_URL`: 자동 설정됨

#### **배포 확인:**
```bash
# Edge Function이 정상 작동하는지 확인
curl -X GET "https://qhrfefcthrogwdwpxkby.supabase.co/functions/v1/youtube-downloader/health" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

**예상 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-24T...",
  "service": "YouTube Downloader API"
}
```

---

### **4. 프론트엔드 설정**

#### **`index.html`의 설정 확인:**
```javascript
const SUPABASE_URL = 'https://qhrfefcthrogwdwpxkby.supabase.co'
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY'

// Edge Function 이름 (Supabase 대시보드에서 확인한 실제 함수 이름)
const functionName = 'youtube-downloader' // ← 여기를 실제 함수 이름으로 변경
```

---

### **5. 일반적인 오류 및 해결**

#### **오류 1: 404 Not Found**
```
POST https://...supabase.co/functions/v1/youtube-downloader/user/login 404
```

**원인:**
- Edge Function이 배포되지 않음
- 함수 이름이 다름

**해결:**
1. Supabase 대시보드 → Edge Functions → 함수 확인
2. 함수가 없으면 `SUPABASE_EDGE_FUNCTION_SETUP.md` 참고하여 배포
3. `index.html`의 `functionName` 변수를 실제 함수 이름으로 수정

---

#### **오류 2: 401 Unauthorized**
```
{"code":401,"message":"Missing authorization header"}
```

**원인:**
- `SUPABASE_ANON_KEY`가 올바르지 않음

**해결:**
1. Supabase 대시보드 → Settings → API → `anon public` 키 복사
2. `index.html`의 `SUPABASE_ANON_KEY` 값 업데이트

---

#### **오류 3: YouTube API 오류**
```
{"error": "YouTube API 키가 설정되지 않았습니다"}
```

**원인:**
- Edge Function의 환경 변수에 `YOUTUBE_API_KEY`가 설정되지 않음

**해결:**
1. Supabase 대시보드 → Edge Functions → `youtube-downloader` → Settings
2. **Secrets** 탭 → `YOUTUBE_API_KEY` 추가
3. 값: `AIzaSyBQ95Zj_awq6A7CrpXXo2eW6GIAcPShQ9Y` (또는 새로운 API 키)

---

### **6. 테스트 순서**

#### **Step 1: Edge Function 확인**
```bash
curl -X GET "https://qhrfefcthrogwdwpxkby.supabase.co/functions/v1/youtube-downloader/health"
```

#### **Step 2: 로그인 테스트**
1. 웹사이트 접속: https://baropoint-debug.github.io/youtube-downloader-supabase/
2. 이메일: `baropoint@gmail.com`
3. 비밀번호: `kimhans74`
4. **로그인** 버튼 클릭
5. **브라우저 개발자 도구** → **Network** 탭 확인

#### **Step 3: 검색 테스트**
1. 로그인 후
2. 검색어 입력 (예: "music")
3. **검색** 버튼 클릭
4. 결과가 표시되는지 확인

#### **Step 4: 다운로드 테스트**
1. 검색 결과에서 비디오 선택
2. **다운로드** 버튼 클릭
3. 다운로드 품질 선택
4. 새 탭에서 YouTube 페이지가 열리는지 확인

---

## 🎯 **다음 단계**

### **현재 상태:**
- ✅ 프론트엔드 코드 수정 완료
- ✅ GitHub Pages 배포 완료
- ⏳ **Edge Function 배포 확인 필요**

### **사용자가 해야 할 일:**
1. **Supabase 대시보드** → **Edge Functions** 확인
2. **`youtube-downloader`** 함수가 있는지 확인
3. **없다면**: `SUPABASE_EDGE_FUNCTION_SETUP.md` 참고하여 배포
4. **있다면**: 환경 변수 (`YOUTUBE_API_KEY`) 확인
5. **웹사이트 테스트**: 로그인 → 검색 → 다운로드

---

## 📞 **추가 도움이 필요하면:**
1. Supabase 대시보드 스크린샷 공유
2. 브라우저 개발자 도구 → Network 탭 오류 공유
3. Edge Functions 목록 확인

