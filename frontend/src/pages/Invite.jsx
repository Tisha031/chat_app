import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import useAuthStore from '../store/authStore'
import toast from 'react-hot-toast'

export default function Invite() {
    const { code } = useParams()
    const { token } = useAuthStore()
    const navigate = useNavigate()
    const [status, setStatus] = useState('joining')

    useEffect(() => {
        if (!token) {
            navigate(`/login?redirect=/invite/${code}`)
            return
        }
        api.post('/invites/use', { code })
            .then(res => {
                toast.success(`Joined #${res.data.room_name}!`)
                navigate('/')
            })
            .catch(err => {
                setStatus('error')
                toast.error(err.response?.data?.detail || 'Invalid invite')
            })
    }, [])

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="text-center">
                <p className="text-5xl mb-4">💬</p>
                {status === 'joining' && (
                    <>
                        <p className="text-white text-xl font-bold">Joining room...</p>
                        <p className="text-gray-400 text-sm mt-2">Please wait</p>
                    </>
                )}
                {status === 'error' && (
                    <>
                        <p className="text-white text-xl font-bold">Invalid or expired invite</p>
                        <button onClick={() => navigate('/')} className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-xl">
                            Go Home
                        </button>
                    </>
                )}
            </div>
        </div>
    )
}