'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Navigation } from './Navigation'
import { MobileMenu } from './MobileMenu'
import { UserMenu } from '@/components/user/Shared/UserMenu'
import { NotificationBell } from '@/components/user/Shared/NotificationBell'
import { useUserStore } from '@/stores/userStore'
import { Menu, Phone } from 'lucide-react'

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { isAuthenticated } = useUserStore()

  return (
    <header className="bg-white border-b border-planning-border sticky top-0 z-50 shadow-sm">
      <Container>
        <div className="flex items-center justify-between py-4">
          {/* Logo */}
          <Link
            href={isAuthenticated ? "/dashboard" : "/"}
            className="flex items-center space-x-2 text-planning-primary hover:opacity-80 transition-opacity"
          >
            <div className="w-8 h-8 bg-planning-primary rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-sm">PE</span>
            </div>
            <span className="font-heading font-semibold text-xl hidden sm:block">
              Planning Explorer
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:block">
            <Navigation />
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {/* Contact Phone - Hidden on mobile when authenticated */}
            <div className={`items-center space-x-2 text-planning-text-light ${
              isAuthenticated ? 'hidden xl:flex' : 'hidden md:flex'
            }`}>
              <Phone className="w-4 h-4" />
              <span className="text-sm">0800 123 4567</span>
            </div>

            {/* Authenticated User Actions */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <NotificationBell />
                <UserMenu />
              </div>
            ) : (
              /* Unauthenticated User Actions */
              <div className="hidden sm:flex items-center space-x-3">
                <Link href="/auth/login">
                  <Button variant="ghost" size="sm" className="text-planning-primary hover:bg-planning-primary/10">
                    Sign In
                  </Button>
                </Link>
                <Link href="/auth/register">
                  <Button size="md" className="bg-planning-primary hover:bg-planning-primary/90 text-white">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 text-planning-primary hover:bg-planning-primary/10 rounded-md transition-colors"
              aria-label="Open mobile menu"
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </div>
      </Container>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
    </header>
  )
}