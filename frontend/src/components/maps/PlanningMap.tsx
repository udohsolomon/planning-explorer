/**
 * PlanningMap Component
 * Interactive Leaflet map with CARTO basemaps
 * PRD REQUIRES: Leaflet.js + CARTO basemaps (NOT Mapbox)
 * Features:
 * - CARTO basemaps (Light, Dark, Voyager)
 * - MarkerClusterGroup for application grouping
 * - Color-coded markers by status
 * - Click marker → popup with application preview
 * - Basemap switcher UI
 * - Map legend
 */

'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { Card } from '@/components/ui/Card'
import type { Application } from '../discovery/ApplicationsTable'

// Dynamically import map components (client-side only)
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
)
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
)
const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
)
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
)

import { CARTO_BASEMAPS, DEFAULT_BASEMAP, UK_CENTER, MAP_CONFIG, getMarkerIcon } from '@/lib/map-config'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Map as MapIcon, Layers, Info } from 'lucide-react'
import Link from 'next/link'

export interface PlanningMapProps {
  applications: Application[]
  center?: [number, number]
  zoom?: number
  height?: string
  showBasemapSwitcher?: boolean
  showLegend?: boolean
  onMarkerClick?: (application: Application) => void
  className?: string
}

export function PlanningMap({
  applications,
  center = UK_CENTER,
  zoom = 12,
  height = '600px',
  showBasemapSwitcher = true,
  showLegend = true,
  onMarkerClick,
  className = '',
}: PlanningMapProps) {
  const [mounted, setMounted] = useState(false)
  const [basemap, setBasemap] = useState<keyof typeof CARTO_BASEMAPS>('voyager')
  const [showSwitcher, setShowSwitcher] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Filter applications with valid coordinates
  const validApplications = applications.filter(
    (app) => app.location && app.location.lat && app.location.lng
  )

  if (!mounted) {
    return (
      <Card className={className}>
        <div
          style={{ height }}
          className="flex items-center justify-center bg-gray-100 rounded-lg"
        >
          <div className="text-center">
            <MapIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Loading map...</p>
          </div>
        </div>
      </Card>
    )
  }

  const selectedBasemap = CARTO_BASEMAPS[basemap]

  return (
    <div className={`relative ${className}`}>
      <Card className="overflow-hidden">
        <div style={{ height }} className="relative">
          <MapContainer
            center={center}
            zoom={zoom}
            {...MAP_CONFIG}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url={selectedBasemap.url}
              attribution={selectedBasemap.attribution}
              maxZoom={selectedBasemap.maxZoom}
            />

            {validApplications.map((app) => (
              <Marker
                key={app.id}
                position={[app.location!.lat, app.location!.lng]}
                icon={getMarkerIcon(app.status)}
                eventHandlers={{
                  click: () => onMarkerClick && onMarkerClick(app),
                }}
              >
                <Popup>
                  <div className="p-2 min-w-[250px]">
                    <h3 className="font-semibold text-sm mb-2">{app.address}</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">Status:</span>
                        <Badge variant={getStatusVariant(app.status)} size="sm">
                          {app.status}
                        </Badge>
                      </div>
                      {app.date && (
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Date:</span>
                          <span className="text-xs">{formatDate(app.date)}</span>
                        </div>
                      )}
                      {app.opportunityScore !== undefined && (
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Score:</span>
                          <span className="text-xs font-medium">{app.opportunityScore}/100</span>
                        </div>
                      )}
                      {app.description && (
                        <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                          {app.description}
                        </p>
                      )}
                      <Link href={`/applications/${app.id}`}>
                        <Button variant="outline" size="sm" className="w-full mt-2">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>

          {/* Basemap Switcher */}
          {showBasemapSwitcher && (
            <div className="absolute top-4 right-4 z-[1000]">
              <div className="relative">
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-white shadow-lg"
                  onClick={() => setShowSwitcher(!showSwitcher)}
                >
                  <Layers className="h-4 w-4 mr-2" />
                  {selectedBasemap.name}
                </Button>

                {showSwitcher && (
                  <div className="absolute top-full right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 p-2 min-w-[150px]">
                    {Object.entries(CARTO_BASEMAPS).map(([key, map]) => (
                      <button
                        key={key}
                        onClick={() => {
                          setBasemap(key as keyof typeof CARTO_BASEMAPS)
                          setShowSwitcher(false)
                        }}
                        className={`w-full text-left px-3 py-2 rounded text-sm hover:bg-gray-100 transition-colors ${
                          basemap === key ? 'bg-gray-100 font-medium' : ''
                        }`}
                      >
                        {map.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Legend */}
          {showLegend && (
            <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg border border-gray-200 p-3">
              <div className="flex items-center gap-2 mb-2">
                <Info className="h-4 w-4 text-gray-600" />
                <h4 className="text-sm font-semibold">Application Status</h4>
              </div>
              <div className="space-y-1.5">
                <LegendItem color="#7CB342" label="Approved" />
                <LegendItem color="#FFCA28" label="Pending" />
                <LegendItem color="#EF5350" label="Rejected" />
                <LegendItem color="#9E9E9E" label="Withdrawn" />
              </div>
              <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-600">
                {validApplications.length} applications shown
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}

/**
 * Legend Item Component
 */
function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="w-3 h-3 rounded-full"
        style={{ backgroundColor: color }}
      />
      <span className="text-xs text-gray-700">{label}</span>
    </div>
  )
}

/**
 * Helper Functions
 */
function getStatusVariant(status: string): 'success' | 'warning' | 'danger' | 'default' {
  const statusLower = status.toLowerCase()
  if (statusLower.includes('approved') || statusLower.includes('permitted')) {
    return 'success'
  }
  if (statusLower.includes('pending') || statusLower.includes('undecided')) {
    return 'warning'
  }
  if (statusLower.includes('rejected') || statusLower.includes('refused')) {
    return 'danger'
  }
  return 'default'
}

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return dateString
  }
}
