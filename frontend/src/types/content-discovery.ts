/**
 * Content Discovery Types
 * TypeScript interfaces for Authority Statistics and Content Discovery features
 */

export interface SectorBreakdown {
  sector: string
  count: number
  percentage: number
}

export interface StatusBreakdown {
  [status: string]: number
}

export interface MonthlyTrend {
  month: string
  total: number
  permitted: number
  rejected: number
  pending: number
}

export interface AuthorityStats {
  authority_name: string
  total_applications_12m: number
  total_applications_all_time: number
  approval_rate: number
  avg_decision_days: number
  active_applications: number
  top_sectors: SectorBreakdown[]
  status_breakdown: StatusBreakdown
  monthly_trend: MonthlyTrend[]
}

export interface AuthorityStatsResponse {
  success: boolean
  data: AuthorityStats
  message?: string
}

export interface AuthorityListItem {
  name: string
  slug: string
  region?: string
  total_applications?: number
  approval_rate?: number
}

/**
 * Sector Statistics Types
 */

export interface RegionalBreakdown {
  region: string
  count: number
  percentage: number
  approval_rate: number
}

export interface AuthorityBreakdown {
  authority_name: string
  count: number
  approval_rate: number
  avg_decision_days: number
}

export interface AgentStats {
  agent_name: string
  applications_count: number
  success_rate: number
  avg_decision_days: number
}

export interface SectorStats {
  sector_name: string
  sector_slug: string
  total_applications_12m: number
  total_applications_all_time: number
  approval_rate: number
  avg_project_value?: number
  avg_decision_days: number
  active_applications: number
  top_region: string
  top_authority: string
  regional_breakdown: RegionalBreakdown[]
  top_authorities: AuthorityBreakdown[]
  top_agents: AgentStats[]
  monthly_trend: MonthlyTrend[]
  growth_rate_12m: number
}

export interface SectorStatsResponse {
  success: boolean
  data: SectorStats
  message?: string
}

export interface Application {
  id: string
  address: string
  status: string
  date: string
  opportunityScore?: number
  decisionDays?: number
  description?: string
  location?: {
    lat: number
    lng: number
  }
  agent?: string
  sector?: string
  authority?: string
}

/**
 * Location Statistics Types
 */

export interface LocationStats {
  location_name: string
  location_type: string // city, town, postcode
  total_applications: number
  authorities: string[]
  sector_breakdown: SectorBreakdown[]
  avg_decision_days: number
  approval_rate: number
  active_applications: number
  most_common_sector: { sector: string; percentage: number } | null
  coordinates: { lat: number; lng: number }
  ai_summary?: string
}

export interface LocationStatsResponse {
  success: boolean
  data: LocationStats
  message?: string
}

export interface NearbyApplicationsResponse {
  success: boolean
  data: {
    applications: Application[]
    total_count: number
  }
  message?: string
}
