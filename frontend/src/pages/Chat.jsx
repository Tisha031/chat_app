import { useNavigate } from 'react-router-dom'
import { useEffect, useState, useCallback } from 'react'
import Sidebar from '../components/sidebar/Sidebar'
import ChatArea from '../components/chat/ChatArea'
import NotificationToast from '../components/chat/NotificationToast'
import useAuthStore from '../store/authStore'
import useRoomStore from '../store/roomStore'
import useNotification from '../hooks/useNotification'

export default function Chat() {
  const { token } = useAuthStore()
  const { setActiveRoom, activeRoom } = useRoomStore()
  const navigate = useNavigate()
  const { notify, requestPermission } = useNotification()
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    if (!token) navigate('/login')
    requestPermission()
  }, [token])

  const addNotification = useCallback((data) => {
    if (activeRoom?.id === data.roomId) return
    const id = Date.now()
    setNotifications(prev => [...prev, { id, ...data }])
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 4000)
  }, [activeRoom])

  return (
    <div className="flex h-screen">
      <Sidebar onRoomSelect={setActiveRoom} />
      <ChatArea onNewMessage={addNotification} />
      <NotificationToast notifications={notifications} />
    </div>
  )
}