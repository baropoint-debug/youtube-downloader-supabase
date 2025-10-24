# 🚀 실제 로컬 다운로드 구현 가이드

## 🚨 **현재 문제점:**

### **❌ 현재 구현:**
```javascript
// 단순히 YouTube URL을 새 탭에서 열기만 함
const downloadWindow = window.open(url, '_blank')
```

**➡️ 실제 파일 다운로드가 되지 않음!**

---

## 🔧 **해결 방법들:**

### **Option 1: 서버 사이드 다운로드 (권장)**

#### **Edge Function에 실제 다운로드 기능 추가:**

```typescript
// supabase_edge_function_FINAL.ts에 추가
if (path === '/download' && method === 'POST') {
  const { videoId, format = '720p' } = await req.json()
  
  try {
    // yt-dlp를 사용한 실제 다운로드
    const { spawn } = require('child_process')
    
    const ytdlp = spawn('yt-dlp', [
      '--format', format,
      '--output', '/tmp/%(title)s.%(ext)s',
      `https://www.youtube.com/watch?v=${videoId}`
    ])
    
    // 다운로드 완료 후 파일 반환
    ytdlp.on('close', (code) => {
      if (code === 0) {
        // 파일을 Supabase Storage에 업로드
        // 또는 직접 파일 스트림 반환
      }
    })
    
  } catch (error) {
    return new Response(JSON.stringify({ error: '다운로드 실패' }))
  }
}
```

#### **장점:**
- ✅ **실제 파일 다운로드**
- ✅ **서버에서 처리** (안정적)
- ✅ **다양한 품질 지원**

#### **단점:**
- ❌ **서버 리소스 사용**
- ❌ **Supabase Edge Function 제한** (15분 타임아웃)
- ❌ **비용 발생**

---

### **Option 2: 클라이언트 사이드 다운로드 (제한적)**

#### **yt-dlp.js 사용:**

```javascript
// index.html에 추가
import ytdl from 'ytdl-core'

async function downloadVideo(videoId, format) {
  try {
    const info = await ytdl.getInfo(videoId)
    const formatInfo = ytdl.chooseFormat(info.formats, { quality: format })
    
    // 브라우저에서 직접 다운로드
    const stream = ytdl(videoId, { format: formatInfo })
    
    // 파일로 저장
    const chunks = []
    stream.on('data', chunk => chunks.push(chunk))
    stream.on('end', () => {
      const blob = new Blob(chunks)
      const url = URL.createObjectURL(blob)
      
      // 다운로드 링크 생성
      const a = document.createElement('a')
      a.href = url
      a.download = `${title}.${formatInfo.container}`
      a.click()
    })
    
  } catch (error) {
    console.error('Download error:', error)
  }
}
```

#### **장점:**
- ✅ **클라이언트에서 직접 처리**
- ✅ **서버 부하 없음**

#### **단점:**
- ❌ **CORS 문제** (YouTube 차단)
- ❌ **브라우저 제한**
- ❌ **안정성 문제**

---

### **Option 3: 하이브리드 방식 (추천)**

#### **1단계: 다운로드 링크 생성**
```javascript
// Edge Function에서 다운로드 가능한 링크 생성
const downloadLinks = {
  '720p': 'https://rr1---sn-4g5e6n7s.googlevideo.com/videoplayback?...',
  '480p': 'https://rr2---sn-4g5e6n7s.googlevideo.com/videoplayback?...',
  '360p': 'https://rr3---sn-4g5e6n7s.googlevideo.com/videoplayback?...'
}
```

#### **2단계: 클라이언트에서 다운로드**
```javascript
function downloadFile(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}
```

---

## 🎯 **추천 구현 방법:**

### **단계별 구현:**

#### **Step 1: 현재 상태 개선**
```javascript
// 현재 다운로드 함수 개선
function startBrowserDownload(url, title, format) {
  try {
    // 파일명 생성
    const filename = `${title.replace(/[^\w\s-]/g, '')}.${format}`
    
    // 다운로드 링크 생성
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.style.display = 'none'
    
    // DOM에 추가하고 클릭
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    showAlert(`${title} 다운로드가 시작되었습니다.`, 'success')
    
  } catch (error) {
    console.error('Download error:', error)
    showAlert('다운로드 중 오류가 발생했습니다.', 'error')
  }
}
```

#### **Step 2: 사용자 지정 경로 추가**
```javascript
// 다운로드 경로 설정
function setDownloadPath() {
  const path = prompt('다운로드 경로를 입력하세요 (예: C:\\Downloads\\Videos):')
  if (path) {
    localStorage.setItem('downloadPath', path)
    showAlert(`다운로드 경로가 설정되었습니다: ${path}`, 'success')
  }
}
```

#### **Step 3: 실제 다운로드 구현**
- **yt-dlp.js** 라이브러리 추가
- **Edge Function**에 실제 다운로드 로직 구현
- **파일 스트림** 반환

---

## 📋 **구현 우선순위:**

### **1단계 (즉시 구현 가능):**
- ✅ **파일명 개선**: 특수문자 제거
- ✅ **다운로드 경로 설정**: 사용자 지정 폴더
- ✅ **다운로드 히스토리**: 로컬 저장

### **2단계 (라이브러리 추가 필요):**
- 🔄 **yt-dlp.js** 추가
- 🔄 **실제 파일 다운로드**
- 🔄 **품질별 다운로드**

### **3단계 (서버 구현 필요):**
- 🔄 **Edge Function** 다운로드 로직
- 🔄 **파일 스트림** 처리
- 🔄 **대용량 파일** 지원

---

## 🚀 **지금 바로 구현할 수 있는 것:**

### **1. 파일명 개선**
### **2. 다운로드 경로 설정**
### **3. 다운로드 히스토리 개선**

**이것부터 구현하시겠습니까?** 🤔
