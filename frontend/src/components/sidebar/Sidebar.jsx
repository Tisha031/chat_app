import { useEffect, useState } from 'react'
import useAuthStore from '../../store/authStore'
import useRoomStore from '../../store/roomStore'
import { getRooms, createRoom, joinRoom } from '../../api/rooms'
import toast from 'react-hot-toast'

export default function Sidebar({ onRoomSelect }) {
  const { user, logout } = useAuthStore()
  const { rooms, setRooms, activeRoom } = useRoomStore()
  const [showModal, setShowModal] = useState(false)
  const [newRoom, setNewRoom] = useState({ name: '', description: '' })

  useEffect(() => {
    fetchRooms()
  }, [])

  const fetchRooms = async () => {
    try {
      const res = await getRooms()
      setRooms(res.data)
    } catch {
      toast.error('Failed to load rooms')
    }
  }

  const handleCreateRoom = async () => {
    try {
      await createRoom({ ...newRoom, is_private: false })
      toast.success('Room created!')
      setShowModal(false)
      setNewRoom({ name: '', description: '' })
      fetchRooms()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create room')
    }
  }

  const handleJoinAndSelect = async (room) => {
    try {
      await joinRoom(room.id)
    } catch {
      // already a member, that's fine
    }
    onRoomSelect(room)
  }

  return (
    <div className="w-64 bg-gray-900 h-screen flex flex-col border-r border-gray-700">

      {/* Workspace Header */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-white font-bold text-lg">💬 ChatApp</h1>
        <p className="text-green-400 text-xs mt-1">● {user?.username}</p>
      </div>

      {/* Channels */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Channels</span>
          <button
            onClick={() => setShowModal(true)}
            className="text-gray-400 hover:text-white text-lg leading-none"
          >
            +
          </button>
        </div>

        {rooms.map((room) => (
          <button
            key={room.id}
            onClick={() => handleJoinAndSelect(room)}
            className={`w-full text-left px-3 py-1.5 rounded text-sm mb-1 transition ${
              activeRoom?.id === room.id
                ? 'bg-purple-600 text-white'
                : 'text-gray-300 hover:bg-gray-700'
            }`}
          >
            # {room.name}
          </button>
        ))}

        {rooms.length === 0 && (
          <p className="text-gray-500 text-xs px-3">No rooms yet. Create one!</p>
        )}
      </div>

      {/* Logout */}
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={logout}
          className="w-full text-left text-gray-400 hover:text-red-400 text-sm transition"
        >
          ← Sign out
        </button>
      </div>

      {/* Create Room Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-xl w-96 shadow-2xl">
            <h2 className="text-white font-bold text-lg mb-4">Create a Channel</h2>

            <input
              type="text"
              placeholder="channel-name"
              value={newRoom.name}
              onChange={(e) => setNewRoom({ ...newRoom, name: e.target.value })}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:outline-none focus:border-purple-500 mb-3"
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={newRoom.description}
              onChange={(e) => setNewRoom({ ...newRoom, description: e.target.value })}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:outline-none focus:border-purple-500 mb-4"
            />

            <div className="flex gap-3">
              <button
                onClick={handleCreateRoom}
                className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition"
              >
                Create
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}