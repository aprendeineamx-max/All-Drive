import { motion } from 'framer-motion'
import { ReactNode } from 'react'
import { CheckCircle2, AlertCircle, Cloud, X } from 'lucide-react'
import React from 'react'

interface GlassCardProps {
    children: ReactNode
    className?: string
    hoverable?: boolean
    onClick?: () => void
}

export function GlassCard({ children, className = '', hoverable = false, onClick }: GlassCardProps) {
    const baseClasses = 'bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 shadow-lg'
    const hoverClasses = hoverable ? 'hover:bg-white/10 cursor-pointer transition-all duration-200' : ''

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className={`${baseClasses} ${hoverClasses} ${className}`}
            onClick={onClick}
        >
            {children}
        </motion.div>
    )
}

interface StatusBadgeProps {
    status: 'active' | 'inactive' | 'warning' | 'error'
    label: string
    pulse?: boolean
}

export function StatusBadge({ status, label, pulse = false }: StatusBadgeProps) {
    const colors = {
        active: 'bg-green-500',
        inactive: 'bg-gray-500',
        warning: 'bg-yellow-500',
        error: 'bg-red-500'
    }

    return (
        <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${colors[status]} ${pulse ? 'animate-pulse' : ''}`} />
            <span className="text-sm text-white/70">{label}</span>
        </div>
    )
}

interface ButtonProps {
    children: ReactNode
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
    loading?: boolean
    onClick?: () => void
    className?: string
}

export function Button({
    children,
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    onClick,
    className = ''
}: ButtonProps) {
    const baseClasses = 'rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2'

    const variants = {
        primary: 'bg-accent-600 hover:bg-accent-500 text-white',
        secondary: 'bg-white/10 hover:bg-white/20 text-white border border-white/10',
        ghost: 'bg-transparent hover:bg-white/10 text-white/80',
        danger: 'bg-red-600 hover:bg-red-500 text-white'
    }

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-sm',
        lg: 'px-6 py-3 text-base'
    }

    const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : ''

    return (
        <button
            onClick={onClick}
            disabled={disabled || loading}
            className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${disabledClasses} ${className}`}
        >
            {loading && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
            )}
            {children}
        </button>
    )
}

interface InputProps {
    value: string
    onChange: (value: string) => void
    placeholder?: string
    type?: string
    disabled?: boolean
    className?: string
}

export function Input({ value, onChange, placeholder, type = 'text', disabled, className = '' }: InputProps) {
    return (
        <input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2 text-white 
        placeholder:text-white/30 focus:outline-none focus:border-accent-500 
        disabled:opacity-50 transition-colors ${className}`}
        />
    )
}

interface SelectProps {
    value: string
    onChange: (value: string) => void
    options: { value: string; label: string }[]
    placeholder?: string
    disabled?: boolean
    className?: string
}

export function Select({ value, onChange, options, placeholder, disabled, className = '' }: SelectProps) {
    return (
        <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            className={`w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2 text-white 
        focus:outline-none focus:border-accent-500 disabled:opacity-50 
        transition-colors appearance-none cursor-pointer ${className}`}
        >
            {placeholder && <option value="">{placeholder}</option>}
            {options.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
        </select>
    )
}

interface ToastProps {
    message: string
    type?: 'success' | 'error' | 'info'
    onClose: () => void
}

export function Toast({ message, type = 'info', onClose }: ToastProps) {
    const icons = {
        success: <CheckCircle2 size={18} className="text-green-400" />,
        error: <AlertCircle size={18} className="text-red-400" />,
        info: <Cloud size={18} className="text-indigo-400" />
    }

    // Auto-dismiss
    React.useEffect(() => {
        const timer = setTimeout(onClose, 3000)
        return () => clearTimeout(timer)
    }, [onClose])

    return (
        <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="flex items-center gap-3 px-4 py-3 bg-[#1a1b26]/90 backdrop-blur-md border border-white/10 rounded-xl shadow-2xl min-w-[300px]"
        >
            {icons[type]}
            <p className="text-sm text-white/90 font-medium">{message}</p>
            <button onClick={onClose} className="ml-auto text-white/30 hover:text-white transition-colors">
                <X size={14} />
            </button>
        </motion.div>
    )
}
