import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import Sidebar from '../components/sidebar/Sidebar'
import ChatArea from '../components/chat/ChatArea'
import useAuthStore from '../store/authStore'
import useRoomStore from '../store/roomStore'

export default function Chat() {
  const { token } = useAuthStore()
  const { setActiveRoom } = useRoomStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!token) navigate('/login')
  }, [token])

  return (
    <div className="flex h-screen">
      <Sidebar onRoomSelect={setActiveRoom} />
      <ChatArea />
    </div>
  )
}