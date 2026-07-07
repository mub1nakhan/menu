import React from 'react'

export default function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const { className = '', ...rest } = props
  return (
    <textarea
      {...rest}
      className={`glass rounded-lg border border-white/10 px-3 py-2 text-sm text-gray-900 w-full ${className}`}
    />
  )
}
