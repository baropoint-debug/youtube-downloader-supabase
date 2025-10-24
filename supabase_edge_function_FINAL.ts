
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

