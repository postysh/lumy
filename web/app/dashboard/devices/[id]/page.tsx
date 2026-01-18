'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Monitor } from 'lucide-react'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { WidgetList } from '@/components/widget-list'
import { QuickActions } from '@/components/quick-actions'

export default function DeviceDetailPage() {
  const params = useParams()
  const deviceId = params.id as string

  const [device, setDevice] = useState<any>(null)
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const fetchDevice = async () => {
    try {
      const response = await fetch(`/api/devices`)
      if (response.ok) {
        const devices = await response.json()
        const foundDevice = devices.find((d: any) => d.device_id === deviceId)
        if (foundDevice) {
          setDevice(foundDevice)
        }
      }
    } catch (error) {
      console.error('Failed to fetch device:', error)
    }
  }

  const fetchStatus = async () => {
    try {
      const response = await fetch(`/api/devices/${deviceId}/status`)
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      }
    } catch (error) {
      console.error('Failed to fetch device status:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDevice()
    fetchStatus()
    // Poll status every 5 seconds
    const interval = setInterval(() => {
      fetchDevice()
      fetchStatus()
    }, 5000)
    return () => clearInterval(interval)
  }, [deviceId])

  if (loading) {
    return (
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/dashboard">Devices</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Loading...</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex flex-1 items-center justify-center">
          <p className="text-muted-foreground">Loading device...</p>
        </div>
      </SidebarInset>
    )
  }

  return (
    <SidebarInset>
      <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard">Devices</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{device?.device_name || deviceId}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <div className="flex flex-1 flex-col gap-6 p-6">
        {/* Device Information */}
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">Device Information</h3>
          
          {/* Info grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-4 text-sm">
            {/* Status */}
            <div>
              <span className="text-muted-foreground">Status</span>
              <div className="mt-1">
                <span className={`inline-flex items-center gap-2 text-sm font-medium ${
                  device?.is_online ? 'text-green-600' : 'text-red-600'
                }`}>
                  <span className={`h-2 w-2 rounded-full ${device?.is_online ? 'bg-green-600' : 'bg-red-600'}`} />
                  {device?.is_online ? 'Online' : 'Offline'}
                </span>
                {device?.last_seen && (
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Last update: {new Date(device.last_seen).toLocaleString('en-US', { 
                      month: 'numeric', 
                      day: 'numeric', 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })} ago
                  </div>
                )}
              </div>
            </div>

            {/* Name */}
            <div>
              <span className="text-muted-foreground">Name</span>
              <div className="mt-1 font-medium">{device?.device_name || 'Unknown'}</div>
            </div>

            {/* Friendly ID / MAC */}
            <div>
              <span className="text-muted-foreground">Friendly ID</span>
              <div className="mt-1 font-medium">
                {device?.device_id?.substring(device.device_id.length - 6).toUpperCase() || 'Unknown'}
              </div>
              <div className="text-xs text-muted-foreground mt-0.5">
                MAC: {status?.system?.mac_address || 'Unknown'}
              </div>
            </div>

            {/* WiFi Signal */}
            <div>
              <span className="text-muted-foreground">WiFi Signal</span>
              <div className="mt-1 font-medium">{status?.system?.wifi_signal || 'Unknown'}</div>
            </div>

            {/* Firmware */}
            <div>
              <span className="text-muted-foreground">Firmware</span>
              <div className="mt-1 font-medium text-xs leading-relaxed">
                {status?.system?.firmware || 'Unknown'}
              </div>
            </div>

            {/* Timezone */}
            <div>
              <span className="text-muted-foreground">Timezone</span>
              <div className="mt-1 font-medium">{status?.system?.timezone || 'UTC'}</div>
            </div>

            {/* Device ID */}
            <div>
              <span className="text-muted-foreground">Device ID</span>
              <div className="mt-1 font-mono text-xs">{device?.device_id || deviceId}</div>
            </div>

            {/* Registered */}
            <div>
              <span className="text-muted-foreground">Registered</span>
              <div className="mt-1 font-medium">
                {device?.registered_at ? new Date(device.registered_at).toLocaleDateString('en-US', {
                  month: 'numeric',
                  day: 'numeric',
                  year: 'numeric'
                }) : 'Unknown'}
              </div>
            </div>

            {/* Refresh Info */}
            <div>
              <span className="text-muted-foreground">Refresh Info</span>
              <div className="mt-1 font-medium">Every 60 seconds</div>
              <div className="text-xs text-muted-foreground mt-0.5">
                Next update: {device?.last_seen ? (() => {
                  const lastSeen = new Date(device.last_seen);
                  const nextUpdate = new Date(lastSeen.getTime() + 60000);
                  return nextUpdate.toLocaleString('en-US', { 
                    month: 'numeric', 
                    day: 'numeric', 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  });
                })() : 'Unknown'}
              </div>
            </div>
          </div>
        </div>

        {/* Display Preview */}
        {device?.display_preview && (
          <div className="mx-auto w-full max-w-4xl">
            <div className="rounded-lg border bg-card overflow-hidden">
              <div className="bg-muted/50 px-4 py-3 border-b">
                <h3 className="text-base font-semibold flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Current Display
                </h3>
              </div>
              <div className="p-6 flex justify-center bg-muted/20">
                <img 
                  src={device.display_preview} 
                  alt="Current display preview" 
                  className="w-full h-auto rounded border shadow-lg"
                />
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <QuickActions onRefresh={fetchStatus} />

        {/* Widget Management */}
        <WidgetList widgets={status?.widgets || {}} />
      </div>
    </SidebarInset>
  )
}
