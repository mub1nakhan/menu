import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger'
}

export default function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  const base = 'inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition'
  const variants: Record<string, string> = {
    primary: 'bg-sky-600 text-white hover:bg-sky-700',
    ghost: 'glass bg-white/10 text-gray-900 hover:bg-white/20',
    danger: 'bg-rose-600 text-white hover:bg-rose-700',
  }

  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}
