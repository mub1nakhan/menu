import React from 'react'

export default function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  const { className = '', children, ...rest } = props
  return (
    <select {...rest} className={`glass rounded-lg border border-white/10 px-3 py-2 text-sm text-gray-900 w-full ${className}`}>
      {children}
    </select>
  )
}
