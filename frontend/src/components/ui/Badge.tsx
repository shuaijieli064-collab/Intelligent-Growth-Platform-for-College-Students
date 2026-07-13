import { forwardRef, type HTMLAttributes } from 'react'

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'accent'
export type BadgeSize = 'sm' | 'md'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  size?: BadgeSize
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-bg-hover text-text-secondary border-border-default',
  success: 'bg-success-light text-success border-success/30',
  warning: 'bg-warning-light text-warning border-warning/30',
  danger: 'bg-danger-light text-danger border-danger/30',
  info: 'bg-info-light text-info border-info/30',
  accent: 'bg-accent-light text-accent-text border-accent-primary/30',
}

const sizeClasses: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'default', size = 'md', className = '', children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={`
          inline-flex items-center justify-center font-medium rounded-md border
          transition-colors duration-200
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${className}
        `}
        {...props}
      >
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'
