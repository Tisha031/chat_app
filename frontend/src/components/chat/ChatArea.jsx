import { useEffect, useRef, useState } from 'react'
import useRoomStore from '../../store/roomStore'
import useAuthStore from '../../store/authStore'
import { getMessages } from '../../api/rooms'

export default function ChatArea() {
  const { activeRoom, messages, addMessage, setMessages } = useRoomStore()
  const { user, token } = useAuthStore()
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(null)
  const wsRef = useRef(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (!activeRoom) return

    // load history
    getMessages(activeRoom.id).then(res => {
      setMessages(res.data.reverse())
    })

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const ws = new WebSocket(`${wsUrl}/ws/${activeRoom.id}?token=${token}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)

      if (data.type === 'message') {
        addMessage(data)
      } else if (data.type === 'typing') {
        if (data.username !== user?.username) {
          setTyping(data.is_typing ? data.username : null)
        }
      } else if (data.type === 'user_joined') {
        addMessage({
          type: 'system',
          content: `${data.username} joined the channel`,
          id: Date.now()
        })
      } else if (data.type === 'user_left') {
        addMessage({
          type: 'system',
          content: `${data.username} left the channel`,
          id: Date.now()
        })
      }
    }

    return () => ws.close()
  }, [activeRoom?.id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return
    wsRef.current.send(JSON.stringify({ type: 'message', content: input }))
    setInput('')
  }

  const handleTyping = (e) => {
    setInput(e.target.value)
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: 'typing', is_typing: true }))
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!activeRoom) {
    return (
      <div className="flex-1 bg-gray-800 flex items-center justify-center">
        <div className="text-center">
          <p className="text-5xl mb-4">💬</p>
          <h2 className="text-white text-xl font-semibold">Welcome to ChatApp</h2>
          <p className="text-gray-400 mt-2">Select a channel to start chatting</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 bg-gray-800 flex flex-col">

      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700 bg-gray-800">
        <h2 className="text-white font-bold text-lg"># {activeRoom.name}</h2>
        {activeRoom.description && (
          <p className="text-gray-400 text-sm">{activeRoom.description}</p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
        {messages.map((msg, i) => {
          if (msg.type === 'system') {
            return (
              <div key={msg.id || i} className="text-center">
                <span className="text-gray-500 text-xs">{msg.content}</span>
              </div>
            )
          }
          const isMe = msg.username === user?.username
          return (
            <div key={msg.id || i} className={`flex gap-3 ${isMe ? 'flex-row-reverse' : ''}`}>
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                {(msg.username || 'U')[0].toUpperCase()}
              </div>
              <div className={`max-w-md ${isMe ? 'items-end' : 'items-start'} flex flex-col`}>
                <span className="text-gray-400 text-xs mb-1">
                  {isMe ? 'You' : msg.username}
                </span>
                <div className={`px-4 py-2 rounded-2xl text-sm ${isMe
                    ? 'bg-purple-600 text-white rounded-tr-none'
                    : 'bg-gray-700 text-gray-100 rounded-tl-none'
                  }`}>
                  {msg.content}
                </div>
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      {/* Typing indicator */}
      {typing && (
        <div className="px-6 pb-1">
          <span className="text-gray-400 text-xs italic">{typing} is typing...</span>
        </div>
      )}

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-700">
        <div className="flex gap-3 items-center bg-gray-700 rounded-xl px-4 py-2">
          <input
            type="text"
            value={input}
            onChange={handleTyping}
            onKeyDown={handleKeyDown}
            placeholder={`Message #${activeRoom.name}`}
            className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-sm"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            className="text-purple-400 hover:text-purple-300 disabled:text-gray-600 transition font-bold"
          >
            ➤
          </button>
        </div>
        <p className="text-gray-600 text-xs mt-1 px-1">Press Enter to send</p>
      </div>
    </div>
  )
}