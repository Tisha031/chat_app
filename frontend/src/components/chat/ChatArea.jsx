import { useEffect, useRef, useState } from 'react'
import useRoomStore from '../../store/roomStore'
import useAuthStore from '../../store/authStore'
import { getMessages } from '../../api/rooms'
import api from '../../api/client'
import useNotification from '../../hooks/useNotification'

export default function ChatArea({ onNewMessage }) {
  const { activeRoom, messages, addMessage, setMessages } = useRoomStore()
  const { user, token } = useAuthStore()
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(null)
  const [loading, setLoading] = useState(false)
  const [onlineUsers, setOnlineUsers] = useState([])
  const [showMentions, setShowMentions] = useState(false)
  const [mentionQuery, setMentionQuery] = useState('')
  const wsRef = useRef(null)
  const bottomRef = useRef(null)
  const typingTimer = useRef(null)
  const inputRef = useRef(null)
  const { notify } = useNotification()

  useEffect(() => {
    if (!activeRoom) return
    setLoading(true)

    getMessages(activeRoom.id)
      .then(res => {
        setMessages(res.data.reverse())
        setLoading(false)
      })
      .catch(() => setLoading(false))

    api.get('/users/online').then(res => setOnlineUsers(res.data)).catch(() => {})

    const ws = new WebSocket(
      `ws://localhost:8000/ws/${activeRoom.id}?token=${token}`
    )
    wsRef.current = ws

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)

      if (data.type === 'message') {
        addMessage(data)
        setTyping(null)

        // 🔔 NOTIFICATION — only for messages from OTHER users
        if (data.username !== user?.username) {
          // play sound + browser notification
          notify(`${data.username}`, data.content, data.username)

          // show popup toast in top right
          onNewMessage?.({
            username: data.username,
            message: data.content,
            room: activeRoom.name,
            roomId: activeRoom.id
          })
        }

      } else if (data.type === 'typing') {
        if (data.username !== user?.username) {
          setTyping(data.is_typing ? data.username : null)
        }
      } else if (data.type === 'user_joined') {
        addMessage({
          type: 'system',
          content: `${data.username} joined 👋`,
          id: Date.now()
        })
      } else if (data.type === 'user_left') {
        addMessage({
          type: 'system',
          content: `${data.username} left`,
          id: Date.now()
        })
      }
    }

    ws.onerror = () => console.log('WebSocket error')

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [activeRoom?.id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleTyping = (e) => {
    const val = e.target.value
    setInput(val)

    const atIndex = val.lastIndexOf('@')
    if (atIndex !== -1) {
      setMentionQuery(val.slice(atIndex + 1))
      setShowMentions(true)
    } else {
      setShowMentions(false)
    }

    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: 'typing', is_typing: true }))
      clearTimeout(typingTimer.current)
      typingTimer.current = setTimeout(() => {
        wsRef.current?.send(JSON.stringify({ type: 'typing', is_typing: false }))
      }, 2000)
    }
  }

  const insertMention = (username) => {
    const atIndex = input.lastIndexOf('@')
    setInput(input.slice(0, atIndex) + `@${username} `)
    setShowMentions(false)
    inputRef.current?.focus()
  }

  const filteredUsers = onlineUsers.filter(u =>
    u.username !== user?.username &&
    u.username.toLowerCase().includes(mentionQuery.toLowerCase())
  )

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return
    wsRef.current.send(JSON.stringify({ type: 'message', content: input }))
    setInput('')
    setShowMentions(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
    if (e.key === 'Escape') setShowMentions(false)
  }

  const renderMessage = (text) => {
    const parts = text.split(/(@\w+)/g)
    return parts.map((part, i) =>
      part.startsWith('@')
        ? <span key={i} className="text-purple-300 font-semibold bg-purple-900/30 px-1 rounded">{part}</span>
        : part
    )
  }

  if (!activeRoom) {
    return (
      <div className="flex-1 bg-gray-800 flex items-center justify-center">
        <div className="text-center max-w-md px-6">
          <p className="text-6xl mb-6">💬</p>
          <h2 className="text-white text-2xl font-bold mb-2">Welcome to ChatApp</h2>
          <p className="text-gray-400 mb-8">Select a channel to start chatting</p>
          <div className="bg-gray-700 rounded-xl p-5 text-left space-y-2">
            <p className="text-gray-300 text-sm font-semibold mb-3">💡 Quick Tips</p>
            <p className="text-gray-400 text-sm">• Click <span className="text-purple-400 font-bold">+</span> to create a new channel</p>
            <p className="text-gray-400 text-sm">• Type <span className="text-purple-400 font-bold">@username</span> to mention someone</p>
            <p className="text-gray-400 text-sm">• Press <span className="text-purple-400 font-bold">Enter</span> to send</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 bg-gray-800 flex flex-col h-screen">

      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700 bg-gray-800 flex items-center gap-3">
        <div>
          <h2 className="text-white font-bold text-lg flex items-center gap-2">
            <span className="text-gray-400">#</span>
            {activeRoom.name}
            {activeRoom.is_locked && <span className="text-sm">🔒</span>}
          </h2>
          {activeRoom.description && (
            <p className="text-gray-400 text-sm">{activeRoom.description}</p>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">

        {loading && (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-400 text-sm">Loading messages...</div>
          </div>
        )}

        {!loading && messages.length === 0 && (
          <div className="flex items-center justify-center py-10">
            <div className="text-center">
              <p className="text-3xl mb-2">👋</p>
              <p className="text-gray-400 text-sm">
                Beginning of <span className="text-white font-medium">#{activeRoom.name}</span>
              </p>
              <p className="text-gray-500 text-xs mt-1">Be the first to send a message!</p>
            </div>
          </div>
        )}

        {!loading && messages.map((msg, i) => {
          if (msg.type === 'system') {
            return (
              <div key={msg.id || i} className="flex items-center gap-3">
                <div className="flex-1 h-px bg-gray-700"></div>
                <span className="text-gray-500 text-xs">{msg.content}</span>
                <div className="flex-1 h-px bg-gray-700"></div>
              </div>
            )
          }

          const isMe = msg.username === user?.username
          const initial = msg.username ? msg.username[0].toUpperCase() : '?'
          const time = msg.timestamp
            ? new Date(msg.timestamp).toLocaleTimeString([], {
                hour: '2-digit', minute: '2-digit'
              })
            : ''

          return (
            <div key={msg.id || i} className={`flex gap-3 ${isMe ? 'flex-row-reverse' : ''}`}>
              <div className="w-9 h-9 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                {initial}
              </div>
              <div className={`max-w-sm flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                <div className={`flex items-center gap-2 mb-1 ${isMe ? 'flex-row-reverse' : ''}`}>
                  <span className="text-gray-300 text-xs font-medium">
                    {isMe ? 'You' : msg.username}
                  </span>
                  <span className="text-gray-600 text-xs">{time}</span>
                </div>
                <div className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  isMe
                    ? 'bg-purple-600 text-white rounded-tr-none'
                    : 'bg-gray-700 text-gray-100 rounded-tl-none'
                }`}>
                  {renderMessage(msg.content)}
                </div>
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      {/* Typing indicator */}
      <div className="px-6 h-5">
        {typing && (
          <p className="text-gray-400 text-xs italic">{typing} is typing...</p>
        )}
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-700 relative">

        {/* @ Mention Dropdown */}
        {showMentions && filteredUsers.length > 0 && (
          <div className="absolute bottom-20 left-6 right-6 bg-gray-700 border border-gray-600 rounded-xl overflow-hidden shadow-xl z-50">
            <div className="px-3 py-2 border-b border-gray-600">
              <p className="text-gray-400 text-xs">Mention someone</p>
            </div>
            {filteredUsers.map((u) => (
              <button
                key={u.user_id}
                onClick={() => insertMention(u.username)}
                className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-600 transition text-left"
              >
                <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold">
                  {u.username[0].toUpperCase()}
                </div>
                <div>
                  <p className="text-white text-sm font-medium">{u.username}</p>
                  <p className="text-green-400 text-xs">● online</p>
                </div>
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-3 items-center bg-gray-700 rounded-xl px-4 py-3 border border-gray-600 focus-within:border-purple-500 transition">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={handleTyping}
            onKeyDown={handleKeyDown}
            placeholder={`Message #${activeRoom.name}... (@ to mention)`}
            className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-sm"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            className="w-8 h-8 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg flex items-center justify-center transition"
          >
            <span className="text-white text-sm">➤</span>
          </button>
        </div>
        <p className="text-gray-600 text-xs mt-2 px-1">Enter to send · @ to mention</p>
      </div>
    </div>
  )
}