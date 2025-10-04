'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { MapPin } from 'lucide-react'

// Dynamically import the MapWrapper to avoid SSR issues
const MapWrapper = dynamic(
  () => import('./MapWrapper').then((mod) => ({ default: mod.MapWrapper })),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[300px] md:h-[400px] rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 flex items-center justify-center">
        <MapPin className="w-12 h-12 text-slate-300 animate-pulse" />
      </div>
    )
  }
)

interface LocationMapProps {
  latitude: number
  longitude: number
  address: string
  postcode?: string
  className?: string
}

export function LocationMap({
  latitude,
  longitude,
  address,
  postcode,
  className = ''
}: LocationMapProps) {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Validate coordinates
  const validLat = latitude && !isNaN(latitude) && latitude >= -90 && latitude <= 90
  const validLon = longitude && !isNaN(longitude) && longitude >= -180 && longitude <= 180

  if (!validLat || !validLon) {
    return (
      <div className={`bg-slate-50 border border-slate-200 rounded-lg p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center text-center">
          <MapPin className="w-12 h-12 text-slate-300 mb-3" />
          <p className="text-sm text-slate-500">
            Location coordinates not available
          </p>
          <p className="text-xs text-slate-400 mt-1">
            {address}
          </p>
        </div>
      </div>
    )
  }

  // Don't render map until mounted to avoid SSR issues
  if (!isMounted) {
    return (
      <div className={`bg-slate-50 border border-slate-200 rounded-lg p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center text-center">
          <MapPin className="w-12 h-12 text-slate-300 mb-3 animate-pulse" />
          <p className="text-sm text-slate-500">
            Loading map...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={`relative ${className}`}>
      <MapWrapper
        latitude={latitude}
        longitude={longitude}
        address={address}
        postcode={postcode}
      />

      {/* Location details below map */}
      <div className="mt-3 flex items-start gap-2 text-sm text-slate-600">
        <MapPin className="w-4 h-4 text-[#043F2E] mt-0.5 flex-shrink-0" />
        <div>
          <p className="font-medium text-slate-800">{address}</p>
          {postcode && <p className="text-xs text-slate-500">{postcode}</p>}
          <p className="text-xs text-slate-400 mt-1">
            Coordinates: {latitude.toFixed(6)}, {longitude.toFixed(6)}
          </p>
        </div>
      </div>
    </div>
  )
}
