// 간단한 테스트용 Edge Function
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

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
    const { method } = req
    const url = new URL(req.url)
    const path = url.pathname

    console.log('Request received:', { method, path })

    // 간단한 응답
    if (path === '/user/login' && method === 'POST') {
      const { email, password } = await req.json()
      
      console.log('Login attempt:', { email, password })
      
      if (email === 'baropoint@gmail.com' && password === 'kimhans74') {
        return new Response(
          JSON.stringify({ 
            success: true, 
            user: {
              id: 'baropoint-user-001',
              email: 'baropoint@gmail.com',
              name: 'BaroPoint'
            },
            message: '로그인 성공'
          }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200 
          }
        )
      } else {
        return new Response(
          JSON.stringify({ error: '이메일 또는 비밀번호가 올바르지 않습니다' }),
          { 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 401 
          }
        )
      }
    }

    // 기본 응답
    return new Response(
      JSON.stringify({ 
        message: 'YouTube Downloader API is running',
        timestamp: new Date().toISOString(),
        path: path,
        method: method
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200 
      }
    )

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500 
      }
    )
  }
})
