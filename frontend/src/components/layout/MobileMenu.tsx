'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Navigation } from './Navigation'
import { X, User, Phone } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MobileMenuProps {
  isOpen: boolean
  onClose: () => void
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          'fixed inset-0 bg-black/60 backdrop-blur-sm z-50 lg:hidden transition-opacity duration-300',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
      />

      {/* Mobile Menu Panel */}
      <div
        className={cn(
          'fixed top-0 right-0 h-full w-80 max-w-[85vw] bg-white shadow-2xl z-50 lg:hidden',
          'transform transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-planning-border">
          <h2 className="font-heading font-semibold text-xl text-planning-primary">
            Menu
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-planning-text-light hover:text-planning-primary hover:bg-planning-primary/10 rounded-md transition-colors"
            aria-label="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-col h-full">
          {/* Navigation */}
          <div className="p-6">
            <Navigation
              orientation="vertical"
              onItemClick={onClose}
              className="space-y-6"
            />
          </div>

          {/* Contact Info */}
          <div className="px-6 py-4 border-t border-planning-border">
            <div className="flex items-center space-x-3 text-planning-text-light mb-4">
              <Phone className="w-5 h-5" />
              <span>0800 123 4567</span>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-auto p-6 space-y-4 border-t border-planning-border">
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={onClose}
            >
              <User className="w-4 h-4 mr-3" />
              Sign In
            </Button>
            <Button
              className="w-full"
              onClick={onClose}
            >
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}