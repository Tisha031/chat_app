import { useEffect, useState } from 'react'

export default function NotificationToast({ notifications }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
      {notifications.map((n) => (
        <div
          key={n.id}
          className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 shadow-2xl flex items-center gap-3 pointer-events-auto animate-slide-in min-w-72"
        >
          <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold flex-shrink-0">
            {n.username?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-semibold">{n.username}</p>
            <p className="text-gray-400 text-xs truncate">#{n.room} · {n.message}</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-purple-400 flex-shrink-0"></div>
        </div>
      ))}
    </div>
  )
}