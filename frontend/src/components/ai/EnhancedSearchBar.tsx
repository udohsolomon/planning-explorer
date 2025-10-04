'use client'

import { useState, useEffect, useRef } from 'react'
import { Search, Brain, Sparkles, MapPin, Filter, History, Zap, MessageSquare, Mic, MicOff } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useSearchStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import { cn } from '@/lib/utils'

interface EnhancedSearchBarProps {
  placeholder?: string
  className?: string
  onSearch?: (query: string, searchType: 'traditional' | 'semantic' | 'natural_language') => void
}

interface SearchInspiration {
  text: string
  highlights: { text: string; color: string }[]
}

const searchInspirations: SearchInspiration[] = [
  {
    text: "Rejected applications in London",
    highlights: [
      { text: "Rejected", color: "text-red-500" },
      { text: "London", color: "text-planning-accent" }
    ]
  },
  {
    text: "Approved developments in Manchester 2025",
    highlights: [
      { text: "Approved", color: "text-green-600" },
      { text: "Manchester", color: "text-planning-accent" },
      { text: "2025", color: "text-planning-highlight" }
    ]
  },
  {
    text: "Housing applications in Sefton",
    highlights: [
      { text: "Housing", color: "text-planning-bright" },
      { text: "Sefton", color: "text-planning-accent" }
    ]
  },
  {
    text: "Developments near SW1A postcode",
    highlights: [
      { text: "Developments", color: "text-planning-bright" },
      { text: "SW1A", color: "text-planning-highlight" }
    ]
  },
  {
    text: "Planning applications in Hull",
    highlights: [
      { text: "Planning applications", color: "text-planning-bright" },
      { text: "Hull", color: "text-planning-accent" }
    ]
  },
  {
    text: "Developments in Cairngorms",
    highlights: [
      { text: "Developments", color: "text-planning-bright" },
      { text: "Cairngorms", color: "text-planning-accent" }
    ]
  },
  {
    text: "Commercial in Aberdeen",
    highlights: [
      { text: "Commercial", color: "text-planning-bright" },
      { text: "Aberdeen", color: "text-planning-accent" }
    ]
  },
  {
    text: "Residential projects in Birmingham 2025",
    highlights: [
      { text: "Residential", color: "text-planning-bright" },
      { text: "Birmingham", color: "text-planning-accent" },
      { text: "2025", color: "text-planning-highlight" }
    ]
  }
]

const recentSearches = [
  "Approved residential in Manchester 2024",
  "Commercial developments near stations",
  "Extension approvals in SW London",
  "High-rise developments Birmingham"
]

export function EnhancedSearchBar({
  placeholder = "Ask anything about UK planning data...",
  className = '',
  onSearch
}: EnhancedSearchBarProps) {
  const [activeTab, setActiveTab] = useState<'recent' | 'inspiration'>('inspiration')
  const [isActive, setIsActive] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)

  const {
    query,
    searchType,
    suggestions,
    isLoadingSuggestions,
    setQuery,
    setSearchType,
    setSuggestions,
    setLoadingSuggestions
  } = useSearchStore()

  useEffect(() => {
    // Initialize speech recognition
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-GB'

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setQuery(transcript)
        setIsListening(false)
      }

      recognitionRef.current.onerror = () => {
        setIsListening(false)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }
  }, [setQuery])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current &&
          !dropdownRef.current.contains(event.target as Node) &&
          inputRef.current &&
          event.target !== inputRef.current) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    if (value.trim()) {
      setShowDropdown(true)
    } else {
      setShowDropdown(false)
    }
  }

  const handleSearch = () => {
    if (query.trim()) {
      onSearch?.(query, searchType)
      setShowDropdown(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    } else if (e.key === 'Escape') {
      setShowDropdown(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    setShowDropdown(false)
    setTimeout(() => onSearch?.(suggestion, searchType), 100)
  }

  const handleVoiceInput = () => {
    if (!recognitionRef.current) return

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  const renderHighlightedText = (inspiration: SearchInspiration) => {
    let text = inspiration.text
    let elements = []
    let lastIndex = 0

    inspiration.highlights.forEach((highlight, index) => {
      const highlightIndex = text.indexOf(highlight.text, lastIndex)
      if (highlightIndex !== -1) {
        // Add text before highlight
        if (highlightIndex > lastIndex) {
          elements.push(text.substring(lastIndex, highlightIndex))
        }
        // Add highlighted text
        elements.push(
          <span key={index} className={`font-semibold ${highlight.color}`}>
            {highlight.text}
          </span>
        )
        lastIndex = highlightIndex + highlight.text.length
      }
    })

    // Add remaining text
    if (lastIndex < text.length) {
      elements.push(text.substring(lastIndex))
    }

    return elements
  }

  return (
    <div className={cn('relative z-50', className)}>
      <div
        className={`relative bg-white rounded-xl border-2 transition-all duration-200 cursor-text ${
          isActive
            ? 'border-planning-primary shadow-lg'
            : 'border-white/20 hover:border-planning-accent'
        }`}
        onClick={() => {
          inputRef.current?.focus()
        }}
      >
        {/* Search Input */}
        <div className="flex items-center p-4 sm:p-6">
          <div className="mr-3 sm:mr-4 text-planning-primary">
            <Search className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            onFocus={() => {
              setIsActive(true)
              if (query.trim() || activeTab === 'inspiration') {
                setShowDropdown(true)
              }
            }}
            onBlur={() => {
              setTimeout(() => setIsActive(false), 100)
            }}
            placeholder={placeholder}
            className="flex-1 text-lg sm:text-xl placeholder-planning-text-light focus:outline-none text-planning-text-dark"
          />

          {query && (
            <button
              onClick={() => setQuery('')}
              className="mr-3 sm:mr-4 p-2 text-planning-text-light hover:text-planning-primary transition-colors"
            >
              ×
            </button>
          )}

          {/* Voice Input Button */}
          <button
            onClick={handleVoiceInput}
            className={cn(
              "mr-3 sm:mr-4 p-2 rounded-lg transition-colors",
              isListening
                ? "bg-red-500 text-white"
                : "text-planning-text-light hover:text-planning-primary hover:bg-planning-primary/5"
            )}
            title={isListening ? "Stop listening" : "Voice search"}
          >
            {isListening ? <MicOff className="w-4 h-4 sm:w-5 sm:h-5" /> : <Mic className="w-4 h-4 sm:w-5 sm:h-5" />}
          </button>

          <Button
            onClick={handleSearch}
            disabled={!query.trim()}
            className="px-4 sm:px-8 py-2 sm:py-3 bg-planning-button text-white hover:bg-planning-primary hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-base sm:text-lg font-semibold"
          >
            <span className="hidden sm:inline">Search</span>
            <Search className="w-4 h-4 sm:hidden" />
          </Button>
        </div>

        {/* AI Enhancement Indicator */}
        {searchType !== 'traditional' && (
          <div className="px-6 pb-3">
            <div className="flex items-center space-x-2 text-sm text-planning-text-light">
              <Zap className="w-4 h-4 text-planning-bright" />
              <span>
                {searchType === 'semantic'
                  ? 'AI-powered semantic search will find similar meanings'
                  : 'Natural language processing will understand your question'
                }
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Search Tabs and Suggestions Dropdown */}
      {showDropdown && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl border border-planning-border shadow-2xl z-50 max-h-[32rem] overflow-auto"
        >
          {/* Tabs */}
          <div className="flex border-b border-planning-border">
            <button
              onClick={() => setActiveTab('recent')}
              className={cn(
                "flex-1 px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm font-medium transition-colors",
                activeTab === 'recent'
                  ? "bg-planning-primary text-white"
                  : "text-planning-text-light hover:text-planning-primary hover:bg-planning-primary/5"
              )}
            >
              <div className="flex items-center justify-center space-x-1 sm:space-x-2">
                <History className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">Your recent searches</span>
                <span className="sm:hidden">Recent</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('inspiration')}
              className={cn(
                "flex-1 px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm font-medium transition-colors",
                activeTab === 'inspiration'
                  ? "bg-planning-primary text-white"
                  : "text-planning-text-light hover:text-planning-primary hover:bg-planning-primary/5"
              )}
            >
              <div className="flex items-center justify-center space-x-1 sm:space-x-2">
                <Sparkles className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">Search inspiration</span>
                <span className="sm:hidden">Inspiration</span>
              </div>
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-4 overflow-y-auto max-h-80">
            {activeTab === 'recent' ? (
              <div className="space-y-2">
                {recentSearches.map((search, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(search)}
                    className="w-full text-left px-4 py-3 hover:bg-planning-primary/5 rounded-lg transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <History className="w-4 h-4 text-planning-text-light flex-shrink-0" />
                      <span className="text-planning-text-dark">{search}</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {searchInspirations.map((inspiration, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(inspiration.text)}
                    className="w-full text-left px-4 py-3 hover:bg-planning-primary/5 rounded-lg transition-colors"
                  >
                    <div className="flex items-start space-x-3">
                      <Sparkles className="w-4 h-4 text-planning-bright flex-shrink-0 mt-0.5" />
                      <span className="text-planning-text-dark leading-relaxed">
                        {renderHighlightedText(inspiration)}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}