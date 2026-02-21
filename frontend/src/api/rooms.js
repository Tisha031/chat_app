import api from './client'

export const getRooms = () => api.get('/rooms')
export const createRoom = (data) => api.post('/rooms', data)
export const joinRoom = (roomId) => api.post(`/rooms/${roomId}/join`)
export const leaveRoom = (roomId) => api.post(`/rooms/${roomId}/leave`)
export const getMessages = (roomId) => api.get(`/rooms/${roomId}/messages`)