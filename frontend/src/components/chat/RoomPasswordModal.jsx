import { useState } from 'react'
import api from '../../api/client'
import toast from 'react-hot-toast'

export default function RoomPasswordModal({ room, onSuccess, onCancel }) {
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await api.post(`/rooms/${room.id}/verify-password`, { password })
      toast.success('Room unlocked!')
      onSuccess()
    } catch {
      toast.error('Wrong password!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-6 rounded-2xl w-96 border border-gray-700 shadow-2xl">
        <div className="text-center mb-6">
          <p className="text-4xl mb-3">🔒</p>
          <h2 className="text-white font-bold text-xl">Locked Channel</h2>
          <p className="text-gray-400 text-sm mt-1">
            <span className="text-purple-400">#{room.name}</span> is password protected
          </p>
        </div>

        <input
          type="password"
          placeholder="Enter room password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          className="w-full px-4 py-3 bg-gray-700 text-white rounded-xl border border-gray-600 focus:outline-none focus:border-purple-500 mb-4"
          autoFocus
        />

        <div className="flex gap-3">
          <button
            onClick={handleSubmit}
            disabled={loading || !password}
            className="flex-1 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-xl font-medium transition"
          >
            {loading ? 'Verifying...' : 'Unlock 🔓'}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-medium transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}