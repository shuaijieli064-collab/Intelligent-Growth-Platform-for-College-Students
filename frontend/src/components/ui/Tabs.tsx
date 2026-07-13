import { useState, type ReactNode } from 'react'

export interface TabsProps {
  defaultValue: string
  children: ReactNode
  className?: string
}

export function Tabs({ defaultValue, children, className = '' }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue)

  const tabs: { value: string; label: ReactNode; content: ReactNode }[] = []

  const childrenArray = Array.isArray(children) ? children : [children]
  childrenArray.forEach((child) => {
    if (child && typeof child === 'object' && 'props' in child) {
      const props = (child as { props: { value: string; label?: ReactNode; children?: ReactNode } }).props
      if (props.value !== undefined) {
        tabs.push({
          value: props.value,
          label: props.label || props.value,
          content: props.children,
        })
      }
    }
  })

  const activeContent = tabs.find((t) => t.value === activeTab)?.content

  return (
    <div className={className}>
      <div className="flex border-b border-border-default mb-4 gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`
              px-5 py-3 text-sm font-medium
              transition-all duration-200 ease-out
              border-b-2 -mb-px
              ${
                activeTab === tab.value
                  ? 'text-accent-text border-accent-primary'
                  : 'text-text-muted border-transparent hover:text-text-secondary hover:border-border-hover'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="animate-fade-in">{activeContent}</div>
    </div>
  )
}

export interface TabProps {
  value: string
  label?: ReactNode
  children?: ReactNode
}

export function Tab(_props: TabProps) {
  return null
}
