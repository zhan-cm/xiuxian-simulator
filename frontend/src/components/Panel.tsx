import { ChevronUp } from 'lucide-react'
import type { ReactNode } from 'react'

interface PanelProps {
  title: string
  icon?: ReactNode
  meta?: string
  children: ReactNode
  className?: string
}

export function Panel({ title, icon, meta, children, className = '' }: PanelProps) {
  return (
    <section className={`jade-panel ${className}`}>
      <header className="panel-heading">
        <div>{icon}<h2>{title}</h2></div>
        <span>{meta}</span>
        <ChevronUp aria-hidden="true" size={17} />
      </header>
      <div className="panel-body">{children}</div>
    </section>
  )
}
