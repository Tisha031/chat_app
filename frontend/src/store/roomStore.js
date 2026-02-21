import { create } from 'zustand'

const useRoomStore = create((set) => ({
  rooms: [],
  activeRoom: null,
  messages: [],

  setRooms: (rooms) => set({ rooms }),
  setActiveRoom: (room) => set({ activeRoom: room, messages: [] }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  setMessages: (messages) => set({ messages }),
}))

export default useRoomStore