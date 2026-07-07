import React from 'react'

export default function Field({ label, children, hint }: { label?: string; children: React.ReactNode; hint?: string }) {
  return (
    <div className="space-y-2">
      {label ? <label className="text-sm font-medium text-gray-700">{label}</label> : null}
      {children}
      {hint ? <p className="text-xs text-gray-500">{hint}</p> : null}
    </div>
  )
}
