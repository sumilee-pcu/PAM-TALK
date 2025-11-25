'use client'

import React, { useEffect, useState } from "react"
import {
  MessageSquare,
  Heart,
  Send,
  User,
  TrendingUp,
  Filter,
  Plus,
  Flag,
  X,
  Image as ImageIcon,
  Users,
  MoreVertical
} from "lucide-react"

// API 엔드포인트
const API_BASE_URL = process.env.NEXT_PUBLIC_COMMUNITY_API_URL || "http://localhost:5002/api/community"

// 타입 정의
interface Post {
  post_id: string
  user_id: string
  username: string
  content: string
  images: string[]
  tags: string[]
  category: string
  created_at: string
  updated_at?: string
  likes_count: number
  comments_count: number
  views_count: number
  is_pinned: boolean
  comments?: Comment[]
}

interface Comment {
  comment_id: string
  post_id: string
  user_id: string
  username: string
  content: string
  parent_comment_id?: string
  created_at: string
  likes_count: number
}

interface Statistics {
  total_posts: number
  total_comments: number
  total_likes: number
  active_users: number
  reaction_rate_24h: number
}

// 시간 포맷 유틸리티
function formatTimeAgo(isoString: string): string {
  const now = new Date()
  const past = new Date(isoString)
  const diffMs = now.getTime() - past.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return '방금 전'
  if (diffMins < 60) return `${diffMins}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  if (diffDays < 7) return `${diffDays}일 전`
  return past.toLocaleDateString('ko-KR')
}

// 게시글 카드 컴포넌트
const PostCard = ({
  post,
  onLike,
  onComment,
  onReport,
  currentUserId
}: {
  post: Post
  onLike: (postId: string) => void
  onComment: (postId: string) => void
  onReport: (postId: string) => void
  currentUserId: string
}) => {
  const [showComments, setShowComments] = useState(false)
  const [commentText, setCommentText] = useState('')
  const [comments, setComments] = useState<Comment[]>(post.comments || [])

  const handleSubmitComment = async () => {
    if (!commentText.trim()) return

    try {
      const response = await fetch(`${API_BASE_URL}/posts/${post.post_id}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUserId,
          username: 'current_user',
          content: commentText
        })
      })

      const data = await response.json()
      if (data.success) {
        setComments([...comments, data.data])
        setCommentText('')
        onComment(post.post_id)
      }
    } catch (error) {
      console.error('댓글 작성 실패:', error)
    }
  }

  return (
    <article className="bg-white dark:bg-neutral-900 rounded-2xl border dark:border-neutral-800 p-6 hover:shadow-md transition-shadow">
      {/* 헤더 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center">
            <User className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <h4 className="font-bold text-emerald-900 dark:text-neutral-100">{post.username}</h4>
            <p className="text-xs text-emerald-600 dark:text-neutral-400">{formatTimeAgo(post.created_at)}</p>
          </div>
        </div>
        <button
          onClick={() => onReport(post.post_id)}
          className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-full"
        >
          <MoreVertical className="w-5 h-5 text-neutral-400" />
        </button>
      </div>

      {/* 카테고리 태그 */}
      {post.category !== 'general' && (
        <span className="inline-block px-3 py-1 bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 text-xs rounded-full mb-3">
          {post.category === 'esg' ? 'ESG' : post.category === 'product' ? '상품' : '질문'}
        </span>
      )}

      {/* 내용 */}
      <p className="text-emerald-900 dark:text-neutral-200 mb-4 whitespace-pre-wrap">{post.content}</p>

      {/* 태그 */}
      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag, idx) => (
            <span key={idx} className="text-sm text-emerald-600 dark:text-emerald-400">
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* 액션 버튼 */}
      <div className="flex items-center gap-6 pt-4 border-t dark:border-neutral-800">
        <button
          onClick={() => onLike(post.post_id)}
          className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
        >
          <Heart className="w-5 h-5" />
          <span className="text-sm">{post.likes_count}</span>
        </button>
        <button
          onClick={() => setShowComments(!showComments)}
          className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
        >
          <MessageSquare className="w-5 h-5" />
          <span className="text-sm">{post.comments_count}</span>
        </button>
        <button
          onClick={() => onReport(post.post_id)}
          className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-orange-600 dark:hover:text-orange-400 transition-colors ml-auto"
        >
          <Flag className="w-5 h-5" />
        </button>
      </div>

      {/* 댓글 섹션 */}
      {showComments && (
        <div className="mt-4 pt-4 border-t dark:border-neutral-800 space-y-4">
          {/* 댓글 목록 */}
          {comments.map((comment) => (
            <div key={comment.comment_id} className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm text-emerald-900 dark:text-neutral-100">{comment.username}</span>
                  <span className="text-xs text-neutral-500 dark:text-neutral-400">{formatTimeAgo(comment.created_at)}</span>
                </div>
                <p className="text-sm text-emerald-900 dark:text-neutral-200">{comment.content}</p>
              </div>
            </div>
          ))}

          {/* 댓글 입력 */}
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center flex-shrink-0">
              <User className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="flex-1 flex gap-2">
              <input
                type="text"
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="댓글을 입력하세요..."
                className="flex-1 px-4 py-2 rounded-full border dark:border-neutral-700 bg-white dark:bg-neutral-800 text-emerald-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                onKeyPress={(e) => e.key === 'Enter' && handleSubmitComment()}
              />
              <button
                onClick={handleSubmitComment}
                className="p-2 rounded-full bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </article>
  )
}

// 메인 커뮤니티 페이지
export default function CommunityPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [stats, setStats] = useState<Statistics | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [showNewPostModal, setShowNewPostModal] = useState(false)
  const [newPostContent, setNewPostContent] = useState('')
  const [newPostCategory, setNewPostCategory] = useState('general')
  const [loading, setLoading] = useState(false)

  const currentUserId = 'USER_002' // 실제로는 로그인한 사용자 ID

  useEffect(() => {
    fetchPosts()
    fetchStatistics()
  }, [selectedCategory])

  const fetchPosts = async () => {
    try {
      const url = selectedCategory === 'all'
        ? `${API_BASE_URL}/posts`
        : `${API_BASE_URL}/posts?category=${selectedCategory}`

      const response = await fetch(url)
      const data = await response.json()

      if (data.success) {
        setPosts(data.data)
      }
    } catch (error) {
      console.error('게시글 조회 실패:', error)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/statistics`)
      const data = await response.json()

      if (data.success) {
        setStats(data.data)
      }
    } catch (error) {
      console.error('통계 조회 실패:', error)
    }
  }

  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUserId,
          username: 'current_user',
          content: newPostContent,
          category: newPostCategory,
          tags: []
        })
      })

      const data = await response.json()

      if (data.success) {
        setPosts([data.data, ...posts])
        setNewPostContent('')
        setShowNewPostModal(false)
        fetchStatistics()
      }
    } catch (error) {
      console.error('게시글 작성 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLike = async (postId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/likes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUserId,
          target_type: 'post',
          target_id: postId
        })
      })

      if (response.ok) {
        fetchPosts()
      }
    } catch (error) {
      console.error('좋아요 실패:', error)
    }
  }

  const handleComment = (postId: string) => {
    fetchPosts()
  }

  const handleReport = async (postId: string) => {
    const confirmed = confirm('이 게시글을 신고하시겠습니까?')
    if (!confirmed) return

    try {
      await fetch(`${API_BASE_URL}/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reporter_id: currentUserId,
          target_type: 'post',
          target_id: postId,
          reason: 'inappropriate_content'
        })
      })
      alert('신고가 접수되었습니다.')
    } catch (error) {
      console.error('신고 실패:', error)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* 헤더 */}
      <header className="bg-white dark:bg-neutral-900 border-b dark:border-neutral-800 sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-emerald-900 dark:text-neutral-100 flex items-center gap-2">
              <Users className="w-7 h-7 text-emerald-600" />
              커뮤니티
            </h1>
            <button
              onClick={() => setShowNewPostModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-full hover:bg-emerald-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              <span>글쓰기</span>
            </button>
          </div>
        </div>
      </header>

      {/* 통계 대시보드 */}
      {stats && (
        <section className="bg-gradient-to-r from-emerald-50 to-emerald-100 dark:from-neutral-900 dark:to-neutral-900 py-8">
          <div className="max-w-5xl mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.total_posts}</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">게시글</p>
              </div>
              <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.active_users}</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">활성 사용자</p>
              </div>
              <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.reaction_rate_24h}%</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">24h 반응률</p>
              </div>
              <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.total_likes}</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">좋아요</p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* 필터 */}
      <section className="max-w-5xl mx-auto px-4 py-6">
        <div className="flex gap-3 overflow-x-auto">
          {['all', 'general', 'esg', 'product', 'question'].map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? 'bg-emerald-600 text-white'
                  : 'bg-white dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
              }`}
            >
              {category === 'all' ? '전체' : category === 'general' ? '일반' : category === 'esg' ? 'ESG' : category === 'product' ? '상품' : '질문'}
            </button>
          ))}
        </div>
      </section>

      {/* 게시글 목록 */}
      <main className="max-w-5xl mx-auto px-4 pb-12">
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard
              key={post.post_id}
              post={post}
              onLike={handleLike}
              onComment={handleComment}
              onReport={handleReport}
              currentUserId={currentUserId}
            />
          ))}

          {posts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-neutral-500 dark:text-neutral-400">아직 게시글이 없습니다.</p>
              <p className="text-sm text-neutral-400 dark:text-neutral-500 mt-2">첫 게시글을 작성해보세요!</p>
            </div>
          )}
        </div>
      </main>

      {/* 글쓰기 모달 */}
      {showNewPostModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-neutral-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-neutral-900 p-6 border-b dark:border-neutral-800 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-emerald-900 dark:text-neutral-100">새 게시글</h2>
              <button
                onClick={() => setShowNewPostModal(false)}
                className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-full"
              >
                <X className="w-6 h-6 text-neutral-600 dark:text-neutral-300" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {/* 카테고리 선택 */}
              <div>
                <label className="block text-sm font-semibold text-emerald-900 dark:text-neutral-100 mb-2">
                  카테고리
                </label>
                <select
                  value={newPostCategory}
                  onChange={(e) => setNewPostCategory(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border dark:border-neutral-700 bg-white dark:bg-neutral-800 text-emerald-900 dark:text-neutral-100"
                >
                  <option value="general">일반</option>
                  <option value="esg">ESG</option>
                  <option value="product">상품</option>
                  <option value="question">질문</option>
                </select>
              </div>

              {/* 내용 */}
              <div>
                <label className="block text-sm font-semibold text-emerald-900 dark:text-neutral-100 mb-2">
                  내용
                </label>
                <textarea
                  value={newPostContent}
                  onChange={(e) => setNewPostContent(e.target.value)}
                  placeholder="무엇을 공유하고 싶으신가요?"
                  rows={6}
                  className="w-full px-4 py-3 rounded-lg border dark:border-neutral-700 bg-white dark:bg-neutral-800 text-emerald-900 dark:text-neutral-100 resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              {/* 버튼 */}
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowNewPostModal(false)}
                  className="px-6 py-2 rounded-full border dark:border-neutral-700 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={handleCreatePost}
                  disabled={loading || !newPostContent.trim()}
                  className="px-6 py-2 rounded-full bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:bg-neutral-400 disabled:cursor-not-allowed"
                >
                  {loading ? '작성 중...' : '게시'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
