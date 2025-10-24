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

    // API 라우팅
    if (path === '/api/health' && method === 'GET') {
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
      const { email, name } = await req.json()
      
      if (!email) {
        return new Response(
          JSON.stringify({ error: '이메일을 입력해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      // 사용자 등록
      const { data, error } = await supabaseClient
        .from('users')
        .insert([{ email, name: name || email.split('@')[0] }])
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
          user: data[0],
          message: '사용자가 성공적으로 등록되었습니다'
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    if (path === '/api/user/login' && method === 'POST') {
      const { email } = await req.json()
      
      if (!email) {
        return new Response(
          JSON.stringify({ error: '이메일을 입력해주세요' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400 
          }
        )
      }

      // 사용자 조회
      const { data, error } = await supabaseClient
        .from('users')
        .select('*')
        .eq('email', email)
        .single()

      if (error || !data) {
        return new Response(
          JSON.stringify({ error: '등록되지 않은 사용자입니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 404 
          }
        )
      }

      return new Response(
        JSON.stringify({ 
          success: true, 
          user: data,
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
