'use client'

import React, { useEffect, useState, useRef } from "react"
import {
  MessageCircle,
  Send,
  User,
  Users,
  Plus,
  X,
  Hash
} from "lucide-react"
import io, { Socket } from 'socket.io-client'

// API 엔드포인트
const API_BASE_URL = process.env.NEXT_PUBLIC_COMMUNITY_API_URL || "http://localhost:5002/api/community"
const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || "http://localhost:5002"

// 타입 정의
interface ChatRoom {
  room_id: string
  room_name: string
  room_type: string
  members: string[]
  created_by: string
  created_at: string
  last_message_at?: string
  is_active: boolean
}

interface ChatMessage {
  message_id: string
  room_id: string
  user_id: string
  username: string
  content: string
  message_type: string
  created_at: string
  is_read: boolean
}

// 시간 포맷 유틸리티
function formatTime(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

// 채팅방 목록 컴포넌트
const RoomList = ({
  rooms,
  selectedRoomId,
  onSelectRoom,
  onCreateRoom
}: {
  rooms: ChatRoom[]
  selectedRoomId: string | null
  onSelectRoom: (roomId: string) => void
  onCreateRoom: () => void
}) => {
  return (
    <div className="h-full flex flex-col bg-white dark:bg-neutral-900 border-r dark:border-neutral-800">
      {/* 헤더 */}
      <div className="p-4 border-b dark:border-neutral-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-emerald-900 dark:text-neutral-100">채팅방</h2>
          <button
            onClick={onCreateRoom}
            className="p-2 hover:bg-emerald-50 dark:hover:bg-neutral-800 rounded-full transition-colors"
          >
            <Plus className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </button>
        </div>
      </div>

      {/* 채팅방 목록 */}
      <div className="flex-1 overflow-y-auto">
        {rooms.map((room) => (
          <button
            key={room.room_id}
            onClick={() => onSelectRoom(room.room_id)}
            className={`w-full p-4 flex items-center gap-3 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors border-b dark:border-neutral-800 ${
              selectedRoomId === room.room_id ? 'bg-emerald-50 dark:bg-emerald-900/20' : ''
            }`}
          >
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center flex-shrink-0">
              <Hash className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold text-emerald-900 dark:text-neutral-100">{room.room_name}</h3>
              <p className="text-sm text-neutral-500 dark:text-neutral-400">
                {room.room_type === 'public' ? '공개' : '비공개'} · {room.members.length}명
              </p>
            </div>
          </button>
        ))}

        {rooms.length === 0 && (
          <div className="p-8 text-center text-neutral-500 dark:text-neutral-400">
            <p>채팅방이 없습니다</p>
            <p className="text-sm mt-2">새 채팅방을 만들어보세요</p>
          </div>
        )}
      </div>
    </div>
  )
}

// 채팅 메시지 컴포넌트
const MessageBubble = ({
  message,
  isOwnMessage
}: {
  message: ChatMessage
  isOwnMessage: boolean
}) => {
  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex gap-2 max-w-[70%] ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}`}>
        {!isOwnMessage && (
          <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center flex-shrink-0">
            <User className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
        )}
        <div>
          {!isOwnMessage && (
            <p className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">{message.username}</p>
          )}
          <div
            className={`px-4 py-2 rounded-2xl ${
              isOwnMessage
                ? 'bg-emerald-600 text-white'
                : 'bg-neutral-100 dark:bg-neutral-800 text-emerald-900 dark:text-neutral-100'
            }`}
          >
            <p>{message.content}</p>
          </div>
          <p className={`text-xs text-neutral-500 dark:text-neutral-400 mt-1 ${isOwnMessage ? 'text-right' : 'text-left'}`}>
            {formatTime(message.created_at)}
          </p>
        </div>
      </div>
    </div>
  )
}

// 메인 채팅 페이지
export default function ChatPage() {
  const [rooms, setRooms] = useState<ChatRoom[]>([])
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [showCreateRoomModal, setShowCreateRoomModal] = useState(false)
  const [newRoomName, setNewRoomName] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isTyping, setIsTyping] = useState(false)
  const [typingUsers, setTypingUsers] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const currentUserId = 'USER_002'
  const currentUsername = 'green_consumer'

  // 자동 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Socket.IO 연결
  useEffect(() => {
    const newSocket = io(SOCKET_URL)
    setSocket(newSocket)

    newSocket.on('connect', () => {
      console.log('Socket connected')
    })

    newSocket.on('disconnect', () => {
      console.log('Socket disconnected')
    })

    return () => {
      newSocket.close()
    }
  }, [])

  // 채팅방 목록 조회
  useEffect(() => {
    fetchRooms()
  }, [])

  // 선택된 채팅방의 메시지 조회
  useEffect(() => {
    if (selectedRoomId) {
      fetchMessages(selectedRoomId)
      joinRoom(selectedRoomId)
    }
  }, [selectedRoomId])

  // Socket 이벤트 리스너
  useEffect(() => {
    if (!socket || !selectedRoomId) return

    socket.on('new_message', (message: ChatMessage) => {
      if (message.room_id === selectedRoomId) {
        setMessages((prev) => [...prev, message])
      }
    })

    socket.on('user_joined', (data: { username: string; message: string }) => {
      console.log(data.message)
    })

    socket.on('user_left', (data: { username: string; message: string }) => {
      console.log(data.message)
    })

    socket.on('user_typing', (data: { username: string }) => {
      setTypingUsers((prev) => [...prev, data.username])
      setTimeout(() => {
        setTypingUsers((prev) => prev.filter((u) => u !== data.username))
      }, 3000)
    })

    return () => {
      socket.off('new_message')
      socket.off('user_joined')
      socket.off('user_left')
      socket.off('user_typing')
    }
  }, [socket, selectedRoomId])

  const fetchRooms = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/rooms?user_id=${currentUserId}`)
      const data = await response.json()

      if (data.success) {
        setRooms(data.data)
        if (data.data.length > 0 && !selectedRoomId) {
          setSelectedRoomId(data.data[0].room_id)
        }
      }
    } catch (error) {
      console.error('채팅방 조회 실패:', error)
    }
  }

  const fetchMessages = async (roomId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/rooms/${roomId}/messages`)
      const data = await response.json()

      if (data.success) {
        setMessages(data.data)
      }
    } catch (error) {
      console.error('메시지 조회 실패:', error)
    }
  }

  const joinRoom = (roomId: string) => {
    if (!socket) return

    socket.emit('join', {
      room_id: roomId,
      username: currentUsername
    })
  }

  const handleCreateRoom = async () => {
    if (!newRoomName.trim()) return

    try {
      const response = await fetch(`${API_BASE_URL}/chat/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: newRoomName,
          created_by: currentUserId,
          room_type: 'public',
          members: [currentUserId]
        })
      })

      const data = await response.json()

      if (data.success) {
        setRooms([...rooms, data.data])
        setNewRoomName('')
        setShowCreateRoomModal(false)
        setSelectedRoomId(data.data.room_id)
      }
    } catch (error) {
      console.error('채팅방 생성 실패:', error)
    }
  }

  const handleSendMessage = () => {
    if (!newMessage.trim() || !socket || !selectedRoomId) return

    socket.emit('send_message', {
      room_id: selectedRoomId,
      user_id: currentUserId,
      username: currentUsername,
      content: newMessage,
      message_type: 'text'
    })

    setNewMessage('')
    setIsTyping(false)
  }

  const handleTyping = () => {
    if (!socket || !selectedRoomId || isTyping) return

    setIsTyping(true)
    socket.emit('typing', {
      room_id: selectedRoomId,
      username: currentUsername
    })

    setTimeout(() => {
      setIsTyping(false)
    }, 3000)
  }

  const selectedRoom = rooms.find((r) => r.room_id === selectedRoomId)

  return (
    <div className="h-screen flex flex-col bg-neutral-50 dark:bg-neutral-900">
      {/* 헤더 */}
      <header className="bg-white dark:bg-neutral-900 border-b dark:border-neutral-800 px-4 py-3">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          <h1 className="text-xl font-bold text-emerald-900 dark:text-neutral-100">실시간 채팅</h1>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 채팅방 목록 (사이드바) */}
        <div className="w-80 hidden md:block">
          <RoomList
            rooms={rooms}
            selectedRoomId={selectedRoomId}
            onSelectRoom={setSelectedRoomId}
            onCreateRoom={() => setShowCreateRoomModal(true)}
          />
        </div>

        {/* 채팅 영역 */}
        <div className="flex-1 flex flex-col bg-white dark:bg-neutral-900">
          {selectedRoom ? (
            <>
              {/* 채팅방 헤더 */}
              <div className="p-4 border-b dark:border-neutral-800">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                    <Hash className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <h2 className="font-bold text-emerald-900 dark:text-neutral-100">{selectedRoom.room_name}</h2>
                    <p className="text-sm text-neutral-500 dark:text-neutral-400">{selectedRoom.members.length}명의 멤버</p>
                  </div>
                </div>
              </div>

              {/* 메시지 목록 */}
              <div className="flex-1 overflow-y-auto p-4">
                {messages.map((message) => (
                  <MessageBubble
                    key={message.message_id}
                    message={message}
                    isOwnMessage={message.user_id === currentUserId}
                  />
                ))}

                {/* 타이핑 인디케이터 */}
                {typingUsers.length > 0 && (
                  <div className="text-sm text-neutral-500 dark:text-neutral-400 italic">
                    {typingUsers.join(', ')}님이 입력 중...
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* 메시지 입력 */}
              <div className="p-4 border-t dark:border-neutral-800">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => {
                      setNewMessage(e.target.value)
                      handleTyping()
                    }}
                    placeholder="메시지를 입력하세요..."
                    className="flex-1 px-4 py-3 rounded-full border dark:border-neutral-700 bg-white dark:bg-neutral-800 text-emerald-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim()}
                    className="px-6 py-3 rounded-full bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:bg-neutral-400 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <MessageCircle className="w-16 h-16 text-neutral-300 dark:text-neutral-700 mx-auto mb-4" />
                <p className="text-neutral-500 dark:text-neutral-400">채팅방을 선택하세요</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 채팅방 생성 모달 */}
      {showCreateRoomModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-neutral-900 rounded-2xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-emerald-900 dark:text-neutral-100">새 채팅방</h2>
              <button
                onClick={() => setShowCreateRoomModal(false)}
                className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-full"
              >
                <X className="w-5 h-5 text-neutral-600 dark:text-neutral-300" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-emerald-900 dark:text-neutral-100 mb-2">
                  채팅방 이름
                </label>
                <input
                  type="text"
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                  placeholder="예: ESG 활동 토론"
                  className="w-full px-4 py-2 rounded-lg border dark:border-neutral-700 bg-white dark:bg-neutral-800 text-emerald-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowCreateRoomModal(false)}
                  className="px-6 py-2 rounded-full border dark:border-neutral-700 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={handleCreateRoom}
                  disabled={!newRoomName.trim()}
                  className="px-6 py-2 rounded-full bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:bg-neutral-400 disabled:cursor-not-allowed"
                >
                  생성
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
