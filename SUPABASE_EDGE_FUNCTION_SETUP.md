# Supabase Edge Function 설정 가이드

## 🚀 **Edge Function 생성 및 배포**

### **Step 1: Supabase 대시보드 접속**
1. **Supabase 대시보드** → **Edge Functions**
2. **"Deploy a new function"** 버튼 클릭

### **Step 2: 함수 생성**
- **Function name**: `youtube-downloader`
- **Template**: **Blank** 선택

### **Step 3: 코드 복사**
다음 코드를 **전체 복사**하여 Edge Function에 붙여넣기:

```typescript
// Supabase Edge Function - YouTube 다운로더 API (수정된 버전)
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
}

serve(async (req) => {
  // CORS 처리
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Supabase 클라이언트 초기화
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    )

    const { method } = req
    const url = new URL(req.url)
    const path = url.pathname

    console.log(`Request: ${method} ${path}`)

    // API 라우팅
    if (path === '/health' && method === 'GET') {
      return new Response(
        JSON.stringify({ 
          status: 'healthy',
          timestamp: new Date().toISOString(),
          service: 'YouTube Downloader API'
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    // 사용자 로그인
    if (path === '/user/login' && method === 'POST') {
      const { email, password } = await req.json()
      
      if (!email || !password) {
        return new Response(
          JSON.stringify({ error: '이메일과 비밀번호를 입력해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      // 사전 등록된 사용자만 허용
      const allowedUsers = [
        { email: 'baropoint@gmail.com', password: 'kimhans74', name: 'BaroPoint' }
      ]

      const allowedUser = allowedUsers.find(user => 
        user.email === email && user.password === password
      )

      if (!allowedUser) {
        return new Response(
          JSON.stringify({ error: '등록되지 않은 사용자입니다. 관리자에게 문의하세요.' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 401 
          }
        )
      }

      // 사용자 정보 반환 (비밀번호 제외)
      const userData = {
        id: 'baropoint-user-001',
        email: allowedUser.email,
        name: allowedUser.name,
        created_at: new Date().toISOString()
      }

      return new Response(
        JSON.stringify({ 
          success: true, 
          user: userData,
          message: '로그인 성공'
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    // YouTube 검색
    if (path === '/search' && method === 'POST') {
      const { query } = await req.json()
      
      if (!query) {
        return new Response(
          JSON.stringify({ error: '검색어를 입력해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      try {
        // YouTube Data API v3를 사용한 검색
        const YOUTUBE_API_KEY = Deno.env.get('YOUTUBE_API_KEY')
        
        if (!YOUTUBE_API_KEY) {
          return new Response(
            JSON.stringify({ error: 'YouTube API 키가 설정되지 않았습니다' }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 500 
            }
          )
        }

        const searchUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=10&key=${YOUTUBE_API_KEY}`
        
        const response = await fetch(searchUrl)
        const data = await response.json()

        if (data.error) {
          return new Response(
            JSON.stringify({ error: data.error.message }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 400 
            }
          )
        }

        const videos = data.items.map((item: any) => ({
          id: item.id.videoId,
          title: item.snippet.title,
          description: item.snippet.description,
          thumbnail: item.snippet.thumbnails.medium.url,
          channel: item.snippet.channelTitle,
          publishedAt: item.snippet.publishedAt,
          url: `https://www.youtube.com/watch?v=${item.id.videoId}`
        }))

        return new Response(
          JSON.stringify({ 
            success: true,
            videos,
            query
          }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200 
          }
        )

      } catch (error) {
        console.error('Search error:', error)
        return new Response(
          JSON.stringify({ error: '검색 중 오류가 발생했습니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500 
          }
        )
      }
    }

    // YouTube URL에서 비디오 정보 가져오기
    if (path === '/video-info' && method === 'POST') {
      const { url } = await req.json()
      
      if (!url) {
        return new Response(
          JSON.stringify({ error: 'YouTube URL을 입력해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      try {
        // URL에서 비디오 ID 추출
        const videoId = extractVideoId(url)
        
        if (!videoId) {
          return new Response(
            JSON.stringify({ error: '유효하지 않은 YouTube URL입니다' }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 400 
            }
          )
        }

        // YouTube Data API v3를 사용한 비디오 정보 가져오기
        const YOUTUBE_API_KEY = Deno.env.get('YOUTUBE_API_KEY')
        
        if (!YOUTUBE_API_KEY) {
          return new Response(
            JSON.stringify({ error: 'YouTube API 키가 설정되지 않았습니다' }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 500 
            }
          )
        }

        const videoUrl = `https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id=${videoId}&key=${YOUTUBE_API_KEY}`
        
        const response = await fetch(videoUrl)
        const data = await response.json()

        if (data.error) {
          return new Response(
            JSON.stringify({ error: data.error.message }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 400 
            }
          )
        }

        if (data.items.length === 0) {
          return new Response(
            JSON.stringify({ error: '비디오를 찾을 수 없습니다' }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 404 
            }
          )
        }

        const video = data.items[0]
        const videoInfo = {
          id: videoId,
          title: video.snippet.title,
          description: video.snippet.description,
          thumbnail: video.snippet.thumbnails.medium.url,
          channel: video.snippet.channelTitle,
          publishedAt: video.snippet.publishedAt,
          duration: video.contentDetails.duration,
          url: `https://www.youtube.com/watch?v=${videoId}`
        }

        return new Response(
          JSON.stringify({ 
            success: true,
            video: videoInfo
          }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200 
          }
        )

      } catch (error) {
        console.error('Video info error:', error)
        return new Response(
          JSON.stringify({ error: '비디오 정보를 가져오는 중 오류가 발생했습니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500 
          }
        )
      }
    }

    // 다운로드 링크 생성 (클라이언트 사이드 다운로드용)
    if (path === '/download-links' && method === 'POST') {
      const { videoId, format = 'mp4' } = await req.json()
      
      if (!videoId) {
        return new Response(
          JSON.stringify({ error: '비디오 ID가 필요합니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      try {
        // 다양한 품질의 다운로드 링크 생성
        const downloadLinks = {
          '720p': `https://www.youtube.com/watch?v=${videoId}&format=720p`,
          '480p': `https://www.youtube.com/watch?v=${videoId}&format=480p`,
          '360p': `https://www.youtube.com/watch?v=${videoId}&format=360p`,
          'audio': `https://www.youtube.com/watch?v=${videoId}&format=audio`
        }

        return new Response(
          JSON.stringify({ 
            success: true,
            videoId,
            downloadLinks,
            message: '다운로드 링크가 생성되었습니다. 클라이언트에서 직접 다운로드하세요.'
          }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200 
          }
        )

      } catch (error) {
        console.error('Download links error:', error)
        return new Response(
          JSON.stringify({ error: '다운로드 링크 생성 중 오류가 발생했습니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500 
          }
        )
      }
    }

    // 404 처리
    return new Response(
      JSON.stringify({ error: 'API 엔드포인트를 찾을 수 없습니다', path, method }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 404 
      }
    )

  } catch (error) {
    console.error('Edge Function error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500 
      }
    )
  }
})

// YouTube URL에서 비디오 ID 추출하는 함수
function extractVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
    /youtube\.com\/watch\?.*v=([^&\n?#]+)/
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) {
      return match[1]
    }
  }
  
  return null
}
```

### **Step 4: 환경 변수 설정**
**Edge Function**에서 다음 환경 변수를 설정해야 합니다:

1. **`YOUTUBE_API_KEY`**: `AIzaSyBQ95Zj_awq6A7CrpXXo2eW6GIAcPShQ9Y`
2. **`SUPABASE_URL`**: `https://qhrfefcthrogwdwpxkby.supabase.co`
3. **`SUPABASE_ANON_KEY`**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4MTg1ODUsImV4cCI6MjA3NTM5NDU4NX0.Do9gajWdwgP8PFSlajAUhZHb024nfNZNnx1IJz9yR5k`

### **Step 5: 배포**
1. **"Deploy"** 버튼 클릭
2. **배포 완료까지 대기** (2-3분)

### **Step 6: 테스트**
배포 완료 후:
1. **웹사이트 새로고침**: `Ctrl + Shift + R`
2. **로그인 테스트**: `baropoint@gmail.com` / `kimhans74`

## 🔧 **문제 해결:**

만약 여전히 404 에러가 발생한다면:

1. **Edge Function URL 확인**: `https://qhrfefcthrogwdwpxkby.supabase.co/functions/v1/youtube-downloader`
2. **브라우저에서 직접 테스트**: `https://qhrfefcthrogwdwpxkby.supabase.co/functions/v1/youtube-downloader/health`
3. **환경 변수 확인**: Edge Function 설정에서 환경 변수가 올바르게 설정되었는지 확인

## 📞 **지원:**

문제가 지속되면 **Supabase 대시보드**에서 **Edge Function 로그**를 확인하여 구체적인 오류 메시지를 파악할 수 있습니다.
