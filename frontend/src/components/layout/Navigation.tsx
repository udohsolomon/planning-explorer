'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

const navigationItems = [
  {
    label: 'Services',
    href: '/services',
    description: 'Our planning intelligence services'
  },
  {
    label: 'About',
    href: '/about',
    description: 'Learn about Planning Explorer'
  },
  {
    label: 'FAQs',
    href: '/faqs',
    description: 'Frequently asked questions'
  },
  {
    label: 'Pricing',
    href: '/pricing',
    description: 'Plans and pricing options'
  }
]

interface NavigationProps {
  className?: string
  orientation?: 'horizontal' | 'vertical'
  onItemClick?: () => void
}

export function Navigation({
  className,
  orientation = 'horizontal',
  onItemClick
}: NavigationProps) {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }

  return (
    <nav className={cn(
      orientation === 'horizontal'
        ? 'flex items-center space-x-8'
        : 'flex flex-col space-y-4',
      className
    )}>
      {navigationItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          onClick={onItemClick}
          className={cn(
            'relative font-medium transition-colors duration-150',
            'hover:text-planning-accent',
            isActive(item.href)
              ? 'text-planning-accent'
              : 'text-planning-primary',
            orientation === 'vertical' && 'py-2'
          )}
        >
          {item.label}
          {/* Active indicator for horizontal nav */}
          {orientation === 'horizontal' && isActive(item.href) && (
            <span className="absolute -bottom-1 left-0 right-0 h-0.5 bg-planning-accent rounded-full" />
          )}
        </Link>
      ))}
    </nav>
  )
}