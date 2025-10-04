'use client'

import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'

interface MapWrapperProps {
  latitude: number
  longitude: number
  address: string
  postcode?: string
}

export function MapWrapper({ latitude, longitude, address, postcode }: MapWrapperProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined' || !mapContainerRef.current) {
      console.log('MapWrapper: Window or container not ready')
      return
    }

    // Check if map already exists and clean it up
    if (mapInstanceRef.current) {
      console.log('MapWrapper: Cleaning up existing map instance')
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }

    // Dynamically import Leaflet only on client side
    const initMap = async () => {
      try {
        console.log('MapWrapper: Initializing map with coords:', latitude, longitude)
        const L = (await import('leaflet')).default

        // Fix default marker icon paths
        delete (L.Icon.Default.prototype as any)._getIconUrl
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: '/leaflet/marker-icon-2x.png',
          iconUrl: '/leaflet/marker-icon.png',
          shadowUrl: '/leaflet/marker-shadow.png',
        })

        // Ensure container is empty before initializing
        if (mapContainerRef.current) {
          // Check if container already has a Leaflet map
          const container = mapContainerRef.current as any
          if (container._leaflet_id) {
            console.log('MapWrapper: Container already has a map, skipping initialization')
            return
          }

          mapContainerRef.current.innerHTML = ''

          // Create the map
          const map = L.map(mapContainerRef.current, {
            center: [latitude, longitude],
            zoom: 18,
            zoomControl: true,
            scrollWheelZoom: false,
          })

          console.log('MapWrapper: Map created successfully')

          // Add tile layer
          L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20,
          }).addTo(map)

          console.log('MapWrapper: Tile layer added')

          // Add marker
          const marker = L.marker([latitude, longitude]).addTo(map)

          console.log('MapWrapper: Marker added')

          // Add popup
          const popupContent = `
            <div style="padding: 8px;">
              <p style="font-weight: 600; font-size: 14px; color: #1e293b; margin-bottom: 4px;">
                ${address}
              </p>
              ${postcode ? `<p style="font-size: 12px; color: #475569;">${postcode}</p>` : ''}
            </div>
          `
          marker.bindPopup(popupContent)

          // Store map instance for cleanup
          mapInstanceRef.current = map

          // Fix map size after initialization
          setTimeout(() => {
            map.invalidateSize()
            console.log('MapWrapper: Map size invalidated')
          }, 100)
        }
      } catch (error) {
        console.error('MapWrapper: Error initializing map:', error)
      }
    }

    initMap()

    // Cleanup function
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [latitude, longitude, address, postcode])

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-[300px] md:h-[400px] rounded-lg overflow-hidden border border-slate-200 shadow-sm print:h-[250px] print:grayscale"
      style={{ zIndex: 1 }}
    />
  )
}
