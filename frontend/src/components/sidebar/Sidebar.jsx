import { useEffect, useState } from 'react'
import useAuthStore from '../../store/authStore'
import useRoomStore from '../../store/roomStore'
import { getRooms, createRoom, joinRoom } from '../../api/rooms'
import api from '../../api/client'
import toast from 'react-hot-toast'
import RoomPasswordModal from '../chat/RoomPasswordModal'

export default function Sidebar({ onRoomSelect }) {
  const { user, logout } = useAuthStore()
  const { rooms, setRooms, activeRoom } = useRoomStore()
  const [showModal, setShowModal] = useState(false)
  const [newRoom, setNewRoom] = useState({ name: '', description: '', is_locked: false, lock_password: '' })
  const [onlineUsers, setOnlineUsers] = useState([])
  const [lockedRoom, setLockedRoom] = useState(null)
  const [dmUsername, setDmUsername] = useState('')
  const [showDmInput, setShowDmInput] = useState(false)
  const [unlockedRooms, setUnlockedRooms] = useState([])

  useEffect(() => {
    fetchRooms()
    fetchOnlineUsers()
    const interval = setInterval(fetchOnlineUsers, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchRooms = async () => {
    try {
      const res = await getRooms()
      setRooms(res.data)
    } catch {
      toast.error('Failed to load rooms')
    }
  }

  const fetchOnlineUsers = async () => {
    try {
      const res = await api.get('/users/online')
      setOnlineUsers(res.data)
    } catch {}
  }

  const handleRoomClick = async (room) => {
    if (room.is_locked && !unlockedRooms.includes(room.id)) {
      setLockedRoom(room)
      return
    }
    try { await joinRoom(room.id) } catch {}
    onRoomSelect(room)
  }

  const handleLockSuccess = () => {
    setUnlockedRooms(prev => [...prev, lockedRoom.id])
    onRoomSelect(lockedRoom)
    setLockedRoom(null)
  }

  const handleCreateRoom = async () => {
    if (!newRoom.name.trim()) { toast.error('Room name required'); return }
    if (newRoom.is_locked && !newRoom.lock_password) { toast.error('Password required for locked room'); return }
    try {
      await createRoom({
        name: newRoom.name.toLowerCase().replace(/\s+/g, '-'),
        description: newRoom.description,
        is_private: false,
        is_locked: newRoom.is_locked,
        lock_password: newRoom.is_locked ? newRoom.lock_password : null
      })
      toast.success('Channel created!')
      setShowModal(false)
      setNewRoom({ name: '', description: '', is_locked: false, lock_password: '' })
      fetchRooms()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create room')
    }
  }

  const handleStartDm = async () => {
    if (!dmUsername.trim()) return
    try {
      const res = await api.post('/rooms/dm/start', { target_username: dmUsername })
      onRoomSelect({ ...res.data.room, dm_target: res.data.target_user.username })
      setDmUsername('')
      setShowDmInput(false)
      toast.success(`DM started with ${res.data.target_user.username}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'User not found')
    }
  }

  const publicRooms = rooms.filter(r => !r.is_direct && r.is_public_server)
  const customRooms = rooms.filter(r => !r.is_direct && !r.is_public_server)

  return (
    <div className="w-64 bg-gray-900 h-screen flex flex-col border-r border-gray-700">

      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-white font-bold text-lg">💬 ChatApp</h1>
        <div className="flex items-center gap-2 mt-1">
          <div className="w-2 h-2 rounded-full bg-green-400"></div>
          <p className="text-green-400 text-xs">{user?.username}</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3">

        {/* Public Servers */}
        {publicRooms.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2 px-2">
              <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">🌍 Public Servers</span>
            </div>
            {publicRooms.map((room) => (
              <button
                key={room.id}
                onClick={() => handleRoomClick(room)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition flex items-center justify-between ${
                  activeRoom?.id === room.id ? 'bg-purple-600 text-white' : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className="flex items-center gap-2">
                  <span className="text-gray-400">#</span>{room.name}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Custom Channels */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2 px-2">
            <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Channels</span>
            <button onClick={() => setShowModal(true)} className="text-gray-400 hover:text-white text-xl transition">+</button>
          </div>

          {customRooms.length === 0 && (
            <p className="text-gray-500 text-xs px-3 py-2">No custom channels yet</p>
          )}

          {customRooms.map((room) => (
            <button
              key={room.id}
              onClick={() => handleRoomClick(room)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition flex items-center justify-between ${
                activeRoom?.id === room.id ? 'bg-purple-600 text-white' : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span className="flex items-center gap-2">
                <span className="text-gray-400">#</span>{room.name}
              </span>
              {room.is_locked && (
                <span title="Password protected">
                  {unlockedRooms.includes(room.id) ? '🔓' : '🔒'}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Direct Messages */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2 px-2">
            <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Direct Messages</span>
            <button
              onClick={() => setShowDmInput(!showDmInput)}
              className="text-gray-400 hover:text-white text-xl transition"
            >
              +
            </button>
          </div>

          {showDmInput && (
            <div className="px-2 mb-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="username"
                  value={dmUsername}
                  onChange={(e) => setDmUsername(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleStartDm()}
                  className="flex-1 px-3 py-1.5 bg-gray-700 text-white text-sm rounded-lg border border-gray-600 focus:outline-none focus:border-purple-500"
                  autoFocus
                />
                <button
                  onClick={handleStartDm}
                  className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition"
                >
                  Go
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Online Users */}
        <div>
          <div className="flex items-center justify-between mb-2 px-2">
            <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Online</span>
            <span className="text-gray-500 text-xs">{onlineUsers.length}</span>
          </div>

          {onlineUsers.length === 0 && (
            <p className="text-gray-500 text-xs px-3">No one online yet</p>
          )}

          {onlineUsers.map((u) => (
            <div key={u.user_id} className="flex items-center gap-2 px-3 py-1.5 rounded-lg">
              <div className="relative">
                <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold">
                  {u.username[0].toUpperCase()}
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-green-400 border-2 border-gray-900"></div>
              </div>
              <span className="text-gray-300 text-sm">{u.username}</span>
            </div>
          ))}
        </div>
      </div>

      {/* User Footer */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-bold">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div>
              <p className="text-white text-sm font-medium">{user?.username}</p>
              <p className="text-green-400 text-xs">● Active</p>
            </div>
          </div>
          <button onClick={logout} className="text-gray-400 hover:text-red-400 text-xs transition">Sign out</button>
        </div>
      </div>

      {/* Create Room Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-2xl w-96 shadow-2xl border border-gray-700">
            <h2 className="text-white font-bold text-xl mb-1">Create a Channel</h2>
            <p className="text-gray-400 text-sm mb-5">Set up a new channel for your team</p>

            <label className="text-gray-300 text-sm font-medium">Channel Name</label>
            <input
              type="text"
              placeholder="e.g. general, random, dev"
              value={newRoom.name}
              onChange={(e) => setNewRoom({ ...newRoom, name: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
              className="w-full mt-1 px-4 py-2.5 bg-gray-700 text-white rounded-xl border border-gray-600 focus:outline-none focus:border-purple-500 mb-4"
            />

            <label className="text-gray-300 text-sm font-medium">Description</label>
            <input
              type="text"
              placeholder="What's this channel about?"
              value={newRoom.description}
              onChange={(e) => setNewRoom({ ...newRoom, description: e.target.value })}
              className="w-full mt-1 px-4 py-2.5 bg-gray-700 text-white rounded-xl border border-gray-600 focus:outline-none focus:border-purple-500 mb-4"
            />

            {/* Lock toggle */}
            <div className="flex items-center justify-between mb-4 bg-gray-700 rounded-xl px-4 py-3">
              <div>
                <p className="text-white text-sm font-medium">🔒 Lock Channel</p>
                <p className="text-gray-400 text-xs">Require password to join</p>
              </div>
              <button
                onClick={() => setNewRoom({ ...newRoom, is_locked: !newRoom.is_locked })}
                className={`w-12 h-6 rounded-full transition-all ${newRoom.is_locked ? 'bg-purple-600' : 'bg-gray-600'}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white mx-0.5 transition-all ${newRoom.is_locked ? 'translate-x-6' : 'translate-x-0'}`}></div>
              </button>
            </div>

            {newRoom.is_locked && (
              <input
                type="password"
                placeholder="Set room password"
                value={newRoom.lock_password}
                onChange={(e) => setNewRoom({ ...newRoom, lock_password: e.target.value })}
                className="w-full px-4 py-2.5 bg-gray-700 text-white rounded-xl border border-purple-500 focus:outline-none mb-4"
              />
            )}

            <div className="flex gap-3">
              <button onClick={handleCreateRoom} className="flex-1 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition">
                Create Channel
              </button>
              <button onClick={() => { setShowModal(false); setNewRoom({ name: '', description: '', is_locked: false, lock_password: '' }) }}
                className="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-medium transition">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Room Password Modal */}
      {lockedRoom && (
        <RoomPasswordModal
          room={lockedRoom}
          onSuccess={handleLockSuccess}
          onCancel={() => setLockedRoom(null)}
        />
      )}
    </div>
  )
}