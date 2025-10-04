export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  company?: string
  role?: string
  phone?: string
  avatar?: string
  subscriptionTier: SubscriptionTier
  createdAt: string
  lastLoginAt?: string
  isEmailVerified: boolean
  isActive: boolean
}

export interface UserProfile {
  id: string
  userId: string
  company?: string
  role?: string
  industry?: string
  interests: string[]
  location?: {
    city?: string
    region?: string
    postcode?: string
  }
  preferences: UserPreferences
  updatedAt: string
}

export interface UserPreferences {
  // AI Personalization
  aiInsightTypes: AIInsightType[]
  aiInsightFrequency: 'realtime' | 'daily' | 'weekly'
  contentPersonalization: boolean

  // Notifications
  emailNotifications: boolean
  browserNotifications: boolean
  alertFrequency: 'instant' | 'daily' | 'weekly'

  // Interface
  theme: 'light' | 'dark' | 'auto'
  compactView: boolean
  defaultSearchRadius: number
  defaultSearchFilters: Record<string, any>

  // Privacy
  dataSharing: boolean
  analytics: boolean
  marketingEmails: boolean
}

export interface SubscriptionTier {
  id: string
  name: 'Free' | 'Professional' | 'Enterprise'
  features: string[]
  limits: {
    searchesPerMonth: number
    alertsLimit: number
    reportsPerMonth: number
    exportLimit: number
    apiCallsPerMonth: number
  }
  price: {
    monthly: number
    annually: number
  }
  billingCycle: 'monthly' | 'annually'
  isActive: boolean
  expiresAt?: string
}

export interface SavedSearch {
  id: string
  userId: string
  name: string
  description?: string
  query: SearchQuery
  filters: Record<string, any>
  category?: string
  tags: string[]
  isPublic: boolean
  lastExecuted?: string
  resultCount?: number
  performance: {
    avgResponseTime: number
    successRate: number
  }
  createdAt: string
  updatedAt: string
}

export interface SearchQuery {
  text: string
  location?: {
    lat: number
    lng: number
    radius: number
  }
  dateRange?: {
    from: string
    to: string
  }
  applicationTypes: string[]
  statuses: string[]
  authorities: string[]
}

export interface Alert {
  id: string
  userId: string
  name: string
  description?: string
  criteria: AlertCriteria
  frequency: 'instant' | 'daily' | 'weekly'
  isActive: boolean
  lastTriggered?: string
  triggerCount: number
  deliveryMethods: ('email' | 'browser' | 'webhook')[]
  webhookUrl?: string
  createdAt: string
  updatedAt: string
}

export interface AlertCriteria {
  searchQuery: SearchQuery
  conditions: {
    newApplications: boolean
    statusChanges: string[]
    keywordMatches: string[]
    thresholds: {
      minimumValue?: number
      maximumValue?: number
    }
  }
}

export interface Notification {
  id: string
  userId: string
  type: 'alert' | 'system' | 'report' | 'recommendation'
  title: string
  message: string
  data?: Record<string, any>
  isRead: boolean
  priority: 'low' | 'medium' | 'high'
  actionUrl?: string
  actionLabel?: string
  createdAt: string
  expiresAt?: string
}

export interface Report {
  id: string
  userId: string
  name: string
  description?: string
  type: 'market_analysis' | 'opportunity_report' | 'custom'
  template?: string
  parameters: Record<string, any>
  schedule?: {
    frequency: 'once' | 'daily' | 'weekly' | 'monthly'
    nextRun?: string
  }
  status: 'draft' | 'generating' | 'completed' | 'failed'
  fileUrl?: string
  fileSize?: number
  createdAt: string
  completedAt?: string
}

export interface Recommendation {
  id: string
  userId: string
  type: 'opportunity' | 'search' | 'alert' | 'insight'
  title: string
  description: string
  confidence: number
  priority: 'low' | 'medium' | 'high'
  data: Record<string, any>
  actionUrl?: string
  actionLabel?: string
  isViewed: boolean
  isActioned: boolean
  createdAt: string
  expiresAt?: string
}

export interface AIInsightType {
  id: string
  name: string
  description: string
  category: 'market' | 'opportunity' | 'risk' | 'trend'
  isEnabled: boolean
}

export interface UsageMetrics {
  period: 'current_month' | 'last_month' | 'current_year'
  searches: {
    used: number
    limit: number
  }
  alerts: {
    used: number
    limit: number
  }
  reports: {
    used: number
    limit: number
  }
  exports: {
    used: number
    limit: number
  }
  apiCalls: {
    used: number
    limit: number
  }
}

export interface UserActivity {
  id: string
  userId: string
  type: 'search' | 'alert_created' | 'report_generated' | 'export' | 'login'
  description: string
  metadata?: Record<string, any>
  createdAt: string
}