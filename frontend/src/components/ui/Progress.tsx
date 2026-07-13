import { forwardRef, type HTMLAttributes } from 'react'

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number
  max?: number
  showLabel?: boolean
  labelPosition?: 'inside' | 'outside'
  variant?: 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

const variantClasses: Record<string, string> = {
  default: 'bg-border-default',
  accent: 'bg-accent-primary',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
  info: 'bg-info',
}

const sizeClasses: Record<string, string> = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-4',
}

export const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  ({
    value,
    max = 100,
    showLabel = false,
    labelPosition = 'outside',
    variant = 'accent',
    size = 'md',
    className = '',
    ...props
  }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

    return (
      <div ref={ref} className={`w-full ${className}`} {...props}>
        {showLabel && labelPosition === 'outside' && (
          <div className="flex justify-between mb-1.5">
            <span className="text-sm font-medium text-text-secondary">进度</span>
            <span className="text-sm font-semibold text-text-primary">{percentage.toFixed(0)}%</span>
          </div>
        )}
        <div
          className={`
            w-full rounded-full overflow-hidden
            bg-bg-active
            ${sizeClasses[size]}
          `}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        >
          <div
            className={`
              h-full rounded-full
              transition-all duration-500 ease-out
              ${variantClasses[variant]}
            `}
            style={{ width: `${percentage}%` }}
          >
            {showLabel && labelPosition === 'inside' && size !== 'sm' && (
              <span className="flex items-center justify-end pr-2 text-xs font-semibold text-white">
                {percentage.toFixed(0)}%
              </span>
            )}
          </div>
        </div>
      </div>
    )
  }
)

Progress.displayName = 'Progress'
