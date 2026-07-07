import React from 'react'

export default function Modal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title?: string; children: React.ReactNode }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative z-10 w-full max-w-2xl rounded-2xl glass p-6">
        {title ? <h3 className="text-lg font-semibold text-gray-900">{title}</h3> : null}
        <div className="mt-4">{children}</div>
        <div className="mt-6 flex justify-end">
          <button onClick={onClose} className="rounded-md px-4 py-2 text-sm bg-white/20">Yopish</button>
        </div>
      </div>
    </div>
  )
}
