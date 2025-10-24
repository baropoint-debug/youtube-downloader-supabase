// Supabase Edge Function - YouTube 다운로더 API
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
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

    // API 라우팅 - 경로에서 /api 제거
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

    if (path === '/api/user/register' && method === 'POST') {
      const { email, password, name } = await req.json()
      
      if (!email || !password) {
        return new Response(
          JSON.stringify({ error: '이메일과 비밀번호를 입력해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      if (password.length < 6) {
        return new Response(
          JSON.stringify({ error: '비밀번호는 6자 이상이어야 합니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      // 비밀번호 해시 생성
      const encoder = new TextEncoder()
      const data = encoder.encode(password)
      const hashBuffer = await crypto.subtle.digest('SHA-256', data)
      const hashArray = Array.from(new Uint8Array(hashBuffer))
      const passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')

      // 사용자 등록
      const { data: userData, error } = await supabaseClient
        .from('users')
        .insert([{ 
          email, 
          password_hash: passwordHash,
          name: name || email.split('@')[0] 
        }])
        .select()

      if (error) {
        return new Response(
          JSON.stringify({ error: error.message }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500 
          }
        )
      }

      return new Response(
        JSON.stringify({ 
          success: true, 
          user: userData[0],
          message: '사용자가 성공적으로 등록되었습니다'
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

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

    if (path === '/api/download' && method === 'POST') {
      const { urls, user_id } = await req.json()
      
      if (!urls || urls.length === 0) {
        return new Response(
          JSON.stringify({ error: '다운로드할 URL을 선택해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      const job_ids = []
      
      for (const url of urls) {
        // 다운로드 작업 생성
        const { data: job, error: jobError } = await supabaseClient
          .from('download_jobs')
          .insert([{
            user_id,
            video_url: url,
            status: 'pending'
          }])
          .select()

        if (jobError) {
          console.error('Job creation error:', jobError)
          continue
        }

        job_ids.push(job[0].id)
      }

      return new Response(
        JSON.stringify({ 
          success: true,
          job_ids,
          message: `${urls.length}개 작업이 생성되었습니다`
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    if (path === '/api/user/favorites' && method === 'GET') {
      const userId = url.searchParams.get('user_id')
      
      if (!userId) {
        return new Response(
          JSON.stringify({ error: '사용자 ID가 필요합니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      const { data, error } = await supabaseClient
        .from('user_favorites')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

      if (error) {
        return new Response(
          JSON.stringify({ error: error.message }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500 
          }
        )
      }

      return new Response(
        JSON.stringify({ favorites: data }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    // 404 처리
    return new Response(
      JSON.stringify({ error: 'API 엔드포인트를 찾을 수 없습니다' }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 404 
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500 
      }
    )
  }
})
