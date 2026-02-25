import { useEffect, useRef } from 'react'
import useAuthStore from '../store/authStore'

const useNotification = () => {
  const { user } = useAuthStore()
  const audioRef = useRef(null)

  useEffect(() => {
    // create notification sound
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    audioRef.current = ctx
  }, [])

  const playSound = () => {
    try {
      const ctx = audioRef.current || new AudioContext()
      const oscillator = ctx.createOscillator()
      const gainNode = ctx.createGain()
      oscillator.connect(gainNode)
      gainNode.connect(ctx.destination)
      oscillator.frequency.setValueAtTime(587, ctx.currentTime)
      oscillator.frequency.setValueAtTime(784, ctx.currentTime + 0.1)
      gainNode.gain.setValueAtTime(0.3, ctx.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3)
      oscillator.start(ctx.currentTime)
      oscillator.stop(ctx.currentTime + 0.3)
    } catch {}
  }

  const notify = (title, body, fromUsername) => {
    if (fromUsername === user?.username) return
    playSound()
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body, icon: '💬' })
    }
  }

  const requestPermission = () => {
    if ('Notification' in window) {
      Notification.requestPermission()
    }
  }

  return { notify, requestPermission }
}

export default useNotification