// Supabase Edge Function - YouTube 다운로더 API (최종 수정 버전)
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
    let path = url.pathname

    // 🔧 경로 정규화: /youtube-downloader 접두사 제거
    if (path.startsWith('/youtube-downloader')) {
      path = path.replace('/youtube-downloader', '')
    }

    console.log(`Request: ${method} ${url.pathname} -> normalized: ${path}`)

    // API 라우팅
    if (path === '/health' && method === 'GET') {
      return new Response(
        JSON.stringify({ 
          status: 'healthy',
          timestamp: new Date().toISOString(),
          service: 'YouTube Downloader API'
        }), 
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json'
          },
          status: 200 
        }
      )
    }

    // 사용자 로그인
    if (path === '/user/login' && method === 'POST') {
      const { email, password } = await req.json()
      
      if (!email || !password) {
        return new Response(
          JSON.stringify({ 
            error: '이메일과 비밀번호를 입력해주세요' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 400
          }
        )
      }

      // 사전 등록된 사용자만 허용
      const allowedUsers = [
        {
          email: 'baropoint@gmail.com',
          password: 'kimhans74',
          name: 'BaroPoint'
        }
      ]

      const allowedUser = allowedUsers.find(
        user => user.email === email && user.password === password
      )

      if (!allowedUser) {
        return new Response(
          JSON.stringify({ 
            error: '등록되지 않은 사용자입니다. 관리자에게 문의하세요.' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
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
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json'
          },
          status: 200
        }
      )
    }

    // YouTube 검색
    if (path === '/search' && method === 'POST') {
      const { query, page = 1, pageSize = 10 } = await req.json()
      
      if (!query) {
        return new Response(
          JSON.stringify({ 
            error: '검색어를 입력해주세요' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 400
          }
        )
      }

      try {
        // YouTube Data API v3를 사용한 검색
        const YOUTUBE_API_KEY = Deno.env.get('YOUTUBE_API_KEY')
        
        if (!YOUTUBE_API_KEY) {
          return new Response(
            JSON.stringify({ 
              error: 'YouTube API 키가 설정되지 않았습니다' 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
              status: 500
            }
          )
        }

        // 페이지네이션 계산
        const maxResults = Math.min(pageSize, 50) // YouTube API 최대 50개
        const startIndex = (page - 1) * maxResults
        
        const searchUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=${maxResults}&key=${YOUTUBE_API_KEY}`
        const response = await fetch(searchUrl)
        const data = await response.json()

        if (data.error) {
          return new Response(
            JSON.stringify({ 
              error: data.error.message 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
              status: 400
            }
          )
        }

        // 비디오 ID 목록 추출
        const videoIds = data.items.map((item: any) => item.id.videoId).join(',')
        
        // videos API로 상세 정보 (duration, viewCount 포함) 가져오기
        const videosUrl = `https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id=${videoIds}&key=${YOUTUBE_API_KEY}`
        const videosResponse = await fetch(videosUrl)
        const videosData = await videosResponse.json()

        if (videosData.error) {
          return new Response(
            JSON.stringify({ 
              error: videosData.error.message 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
              status: 400
            }
          )
        }

        const videos = videosData.items.map((item: any) => ({
          id: item.id,
          title: item.snippet.title,
          description: item.snippet.description,
          thumbnail: item.snippet.thumbnails.medium.url,
          channel: item.snippet.channelTitle,
          publishedAt: item.snippet.publishedAt,
          duration: item.contentDetails.duration, // ISO 8601 형식 (예: PT4M13S)
          viewCount: parseInt(item.statistics.viewCount || '0'),
          likeCount: parseInt(item.statistics.likeCount || '0'),
          commentCount: parseInt(item.statistics.commentCount || '0'),
          url: `https://www.youtube.com/watch?v=${item.id}`
        }))

        return new Response(
          JSON.stringify({ 
            success: true,
            videos,
            query,
            pagination: {
              currentPage: page,
              pageSize: maxResults,
              totalResults: data.pageInfo?.totalResults || 0,
              hasNextPage: !!data.nextPageToken,
              hasPrevPage: page > 1,
              nextPageToken: data.nextPageToken,
              prevPageToken: data.prevPageToken
            }
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 200
          }
        )
      } catch (error) {
        console.error('Search error:', error)
        return new Response(
          JSON.stringify({ 
            error: '검색 중 오류가 발생했습니다' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
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
          JSON.stringify({ 
            error: 'YouTube URL을 입력해주세요' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 400
          }
        )
      }

      try {
        // URL에서 비디오 ID 추출
        const videoId = extractVideoId(url)
        
        if (!videoId) {
          return new Response(
            JSON.stringify({ 
              error: '유효하지 않은 YouTube URL입니다' 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
              status: 400
            }
          )
        }

        // YouTube Data API v3를 사용한 비디오 정보 가져오기
        const YOUTUBE_API_KEY = Deno.env.get('YOUTUBE_API_KEY')
        
        if (!YOUTUBE_API_KEY) {
          return new Response(
            JSON.stringify({ 
              error: 'YouTube API 키가 설정되지 않았습니다' 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
              status: 500
            }
          )
        }

        const videoUrl = `https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id=${videoId}&key=${YOUTUBE_API_KEY}`
        const response = await fetch(videoUrl)
        const data = await response.json()

        if (data.error) {
          return new Response(
            JSON.stringify({ 
              error: data.error.message 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
              status: 400
            }
          )
        }

        if (data.items.length === 0) {
          return new Response(
            JSON.stringify({ 
              error: '비디오를 찾을 수 없습니다' 
            }), 
            {
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json'
              },
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
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 200
          }
        )
      } catch (error) {
        console.error('Video info error:', error)
        return new Response(
          JSON.stringify({ 
            error: '비디오 정보를 가져오는 중 오류가 발생했습니다' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
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
          JSON.stringify({ 
            error: '비디오 ID가 필요합니다' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
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
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 200
          }
        )
      } catch (error) {
        console.error('Download links error:', error)
        return new Response(
          JSON.stringify({ 
            error: '다운로드 링크 생성 중 오류가 발생했습니다' 
          }), 
          {
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json'
            },
            status: 500
          }
        )
      }
    }

    // 404 처리
    return new Response(
      JSON.stringify({ 
        error: 'API 엔드포인트를 찾을 수 없습니다',
        path,
        method,
        originalPath: url.pathname
      }), 
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        },
        status: 404
      }
    )
  } catch (error: any) {
    console.error('Edge Function error:', error)
    return new Response(
      JSON.stringify({ 
        error: error.message 
      }), 
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        },
        status: 500
      }
    )
  }
})

// YouTube URL에서 비디오 ID 추출하는 함수
function extractVideoId(url: string): string | null {
  try {
    // YouTube URL 패턴들
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /youtube\.com\/watch\?.*v=([^&\n?#]+)/
    ]
    
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match && match[1]) {
        return match[1]
      }
    }
    
    return null
  } catch (error) {
    console.error('extractVideoId error:', error)
    return null
  }
}

