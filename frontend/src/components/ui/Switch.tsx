import { useState, forwardRef } from 'react'

export interface SwitchProps {
  checked?: boolean
  defaultChecked?: boolean
  onChange?: (checked: boolean) => void
  disabled?: boolean
  size?: 'sm' | 'md'
  label?: string
  id?: string
}

export const Switch = forwardRef<HTMLButtonElement, SwitchProps>(
  ({
    checked: controlledChecked,
    defaultChecked = false,
    onChange,
    disabled = false,
    size = 'md',
    label,
    id,
  }, ref) => {
    const [internalChecked, setInternalChecked] = useState(defaultChecked)
    const isControlled = controlledChecked !== undefined
    const checked = isControlled ? controlledChecked : internalChecked

    const toggle = () => {
      if (disabled) return
      const newChecked = !checked
      if (!isControlled) {
        setInternalChecked(newChecked)
      }
      onChange?.(newChecked)
    }

    const sizeStyles = size === 'sm'
      ? { track: 'w-9 h-5', thumb: 'w-4 h-4', translate: 'translate-x-4' }
      : { track: 'w-11 h-6', thumb: 'w-5 h-5', translate: 'translate-x-5' }

    return (
      <label
        htmlFor={id}
        className={`inline-flex items-center gap-2.5 ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <button
          ref={ref}
          id={id}
          type="button"
          role="switch"
          aria-checked={checked}
          disabled={disabled}
          onClick={toggle}
          className={`
            relative inline-flex items-center rounded-full
            transition-colors duration-200 ease-out
            focus:outline-none focus:ring-2 focus:ring-accent-primary/30 focus:ring-offset-2 focus:ring-offset-bg-surface
            ${checked ? 'bg-accent-primary' : 'bg-border-focus'}
            ${sizeStyles.track}
            ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          <span
            className={`
              inline-block bg-white rounded-full shadow-md
              transition-transform duration-200 ease-out
              ${sizeStyles.thumb}
              ${checked ? sizeStyles.translate : 'translate-x-0.5'}
            `}
          />
        </button>
        {label && (
          <span className="text-sm text-text-primary">{label}</span>
        )}
      </label>
    )
  }
)

Switch.displayName = 'Switch'
