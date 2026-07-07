import React from 'react'

export default function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  const { className = '', ...rest } = props
  return (
    <input
      {...rest}
      className={`glass rounded-lg border border-white/10 px-3 py-2 text-sm text-gray-900 w-full ${className}`}
    />
  )
}
