import React from 'react'
import Button from './button'

interface Action { title: string; href?: string; onClick?: () => void }

export default function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: Action[] }) {
  return (
    <div className="mb-6 flex items-center justify-between glass p-4 rounded-2xl">
      <div>
        <p className="text-sm font-semibold text-gray-600">{subtitle}</p>
        <h2 className="mt-1 text-2xl font-semibold text-gray-900">{title}</h2>
      </div>
      <div className="flex items-center gap-3">
        {actions?.map((a) => (
          a.href ? (
            <a key={a.title} href={a.href}><Button>{a.title}</Button></a>
          ) : (
            <Button key={a.title} onClick={a.onClick}>{a.title}</Button>
          )
        ))}
      </div>
    </div>
  )
}
