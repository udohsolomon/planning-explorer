import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import {
  User,
  UserProfile,
  SubscriptionTier,
  SavedSearch,
  Alert,
  Report,
  Notification,
  Recommendation,
  UserPreferences,
  UsageMetrics,
  UserActivity
} from '@/types/user'

interface UserState {
  // Authentication
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean

  // User Data
  profile: UserProfile | null
  subscription: SubscriptionTier | null
  preferences: UserPreferences | null

  // User Features
  savedSearches: SavedSearch[]
  alerts: Alert[]
  reports: Report[]
  notifications: Notification[]
  recommendations: Recommendation[]

  // Analytics
  usageMetrics: UsageMetrics | null
  recentActivity: UserActivity[]

  // UI State
  unreadNotifications: number
  sidebarCollapsed: boolean

  // Actions - Authentication
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  login: (user: User) => void
  logout: () => void

  // Actions - Profile
  updateProfile: (profile: Partial<UserProfile>) => void
  updatePreferences: (preferences: Partial<UserPreferences>) => void

  // Actions - Saved Searches
  addSavedSearch: (search: SavedSearch) => void
  updateSavedSearch: (id: string, updates: Partial<SavedSearch>) => void
  deleteSavedSearch: (id: string) => void
  setSavedSearches: (searches: SavedSearch[]) => void

  // Actions - Alerts
  addAlert: (alert: Alert) => void
  updateAlert: (id: string, updates: Partial<Alert>) => void
  deleteAlert: (id: string) => void
  toggleAlert: (id: string) => void
  setAlerts: (alerts: Alert[]) => void

  // Actions - Reports
  addReport: (report: Report) => void
  updateReport: (id: string, updates: Partial<Report>) => void
  deleteReport: (id: string) => void
  setReports: (reports: Report[]) => void

  // Actions - Notifications
  addNotification: (notification: Notification) => void
  markNotificationRead: (id: string) => void
  markAllNotificationsRead: () => void
  deleteNotification: (id: string) => void
  setNotifications: (notifications: Notification[]) => void

  // Actions - Recommendations
  addRecommendation: (recommendation: Recommendation) => void
  markRecommendationViewed: (id: string) => void
  markRecommendationActioned: (id: string) => void
  dismissRecommendation: (id: string) => void
  setRecommendations: (recommendations: Recommendation[]) => void

  // Actions - Analytics
  setUsageMetrics: (metrics: UsageMetrics) => void
  addActivity: (activity: UserActivity) => void
  setRecentActivity: (activities: UserActivity[]) => void

  // Actions - UI
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial State
        user: null,
        isAuthenticated: false,
        isLoading: false,
        profile: null,
        subscription: null,
        preferences: null,
        savedSearches: [],
        alerts: [],
        reports: [],
        notifications: [],
        recommendations: [],
        usageMetrics: null,
        recentActivity: [],
        unreadNotifications: 0,
        sidebarCollapsed: false,

        // Authentication Actions
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        setLoading: (isLoading) => set({ isLoading }),

        login: (user) => set({
          user,
          isAuthenticated: true,
          isLoading: false
        }),

        logout: () => set({
          user: null,
          isAuthenticated: false,
          profile: null,
          subscription: null,
          preferences: null,
          savedSearches: [],
          alerts: [],
          reports: [],
          notifications: [],
          recommendations: [],
          usageMetrics: null,
          recentActivity: [],
          unreadNotifications: 0
        }),

        // Profile Actions
        updateProfile: (profileUpdates) => set((state) => ({
          profile: state.profile ? { ...state.profile, ...profileUpdates } : null
        })),

        updatePreferences: (preferenceUpdates) => set((state) => ({
          preferences: state.preferences ? { ...state.preferences, ...preferenceUpdates } : null
        })),

        // Saved Searches Actions
        addSavedSearch: (search) => set((state) => ({
          savedSearches: [search, ...state.savedSearches]
        })),

        updateSavedSearch: (id, updates) => set((state) => ({
          savedSearches: state.savedSearches.map(search =>
            search.id === id ? { ...search, ...updates } : search
          )
        })),

        deleteSavedSearch: (id) => set((state) => ({
          savedSearches: state.savedSearches.filter(search => search.id !== id)
        })),

        setSavedSearches: (savedSearches) => set({ savedSearches }),

        // Alerts Actions
        addAlert: (alert) => set((state) => ({
          alerts: [alert, ...state.alerts]
        })),

        updateAlert: (id, updates) => set((state) => ({
          alerts: state.alerts.map(alert =>
            alert.id === id ? { ...alert, ...updates } : alert
          )
        })),

        deleteAlert: (id) => set((state) => ({
          alerts: state.alerts.filter(alert => alert.id !== id)
        })),

        toggleAlert: (id) => set((state) => ({
          alerts: state.alerts.map(alert =>
            alert.id === id ? { ...alert, isActive: !alert.isActive } : alert
          )
        })),

        setAlerts: (alerts) => set({ alerts }),

        // Reports Actions
        addReport: (report) => set((state) => ({
          reports: [report, ...state.reports]
        })),

        updateReport: (id, updates) => set((state) => ({
          reports: state.reports.map(report =>
            report.id === id ? { ...report, ...updates } : report
          )
        })),

        deleteReport: (id) => set((state) => ({
          reports: state.reports.filter(report => report.id !== id)
        })),

        setReports: (reports) => set({ reports }),

        // Notifications Actions
        addNotification: (notification) => set((state) => {
          const newNotifications = [notification, ...state.notifications]
          return {
            notifications: newNotifications,
            unreadNotifications: newNotifications.filter(n => !n.isRead).length
          }
        }),

        markNotificationRead: (id) => set((state) => {
          const updatedNotifications = state.notifications.map(notification =>
            notification.id === id ? { ...notification, isRead: true } : notification
          )
          return {
            notifications: updatedNotifications,
            unreadNotifications: updatedNotifications.filter(n => !n.isRead).length
          }
        }),

        markAllNotificationsRead: () => set((state) => ({
          notifications: state.notifications.map(notification => ({ ...notification, isRead: true })),
          unreadNotifications: 0
        })),

        deleteNotification: (id) => set((state) => {
          const updatedNotifications = state.notifications.filter(notification => notification.id !== id)
          return {
            notifications: updatedNotifications,
            unreadNotifications: updatedNotifications.filter(n => !n.isRead).length
          }
        }),

        setNotifications: (notifications) => set({
          notifications,
          unreadNotifications: notifications.filter(n => !n.isRead).length
        }),

        // Recommendations Actions
        addRecommendation: (recommendation) => set((state) => ({
          recommendations: [recommendation, ...state.recommendations]
        })),

        markRecommendationViewed: (id) => set((state) => ({
          recommendations: state.recommendations.map(rec =>
            rec.id === id ? { ...rec, isViewed: true } : rec
          )
        })),

        markRecommendationActioned: (id) => set((state) => ({
          recommendations: state.recommendations.map(rec =>
            rec.id === id ? { ...rec, isActioned: true } : rec
          )
        })),

        dismissRecommendation: (id) => set((state) => ({
          recommendations: state.recommendations.filter(rec => rec.id !== id)
        })),

        setRecommendations: (recommendations) => set({ recommendations }),

        // Analytics Actions
        setUsageMetrics: (usageMetrics) => set({ usageMetrics }),

        addActivity: (activity) => set((state) => ({
          recentActivity: [activity, ...state.recentActivity.slice(0, 49)] // Keep last 50
        })),

        setRecentActivity: (recentActivity) => set({ recentActivity }),

        // UI Actions
        toggleSidebar: () => set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed
        })),

        setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed })
      }),
      {
        name: 'user-store',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          preferences: state.preferences,
          sidebarCollapsed: state.sidebarCollapsed
        })
      }
    ),
    { name: 'user-store' }
  )
)