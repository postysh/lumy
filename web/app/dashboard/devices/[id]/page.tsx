'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Monitor, Wifi, Grid3x3, Settings, ArrowLeft } from 'lucide-react'
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
import { Button } from "@/components/ui/button"
import { StatusCard } from '@/components/status-card'
import { WidgetList } from '@/components/widget-list'
import { QuickActions } from '@/components/quick-actions'

export default function DeviceDetailPage() {
  const params = useParams()
  const router = useRouter()
  const deviceId = params.id as string

  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

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
    fetchStatus()
    // Poll every 5 seconds
    const interval = setInterval(fetchStatus, 5000)
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
              <BreadcrumbPage>{deviceId}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <div className="flex flex-1 flex-col gap-4 p-6">
        {/* Back button and title */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/dashboard')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <div>
            <h2 className="text-2xl font-bold">{status?.device_id || deviceId}</h2>
            <p className="text-muted-foreground">Device Overview</p>
          </div>
        </div>

        {/* Status Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <StatusCard
            title="Display Status"
            value={status?.status === 'online' ? 'Online' : 'Offline'}
            icon={<Monitor className="w-6 h-6" />}
            status={status?.status === 'online' ? 'success' : 'error'}
            description={
              status?.last_refresh
                ? `Last refresh: ${new Date(status.last_refresh).toLocaleTimeString()}`
                : 'Not connected'
            }
          />

          <StatusCard
            title="System Info"
            value={status?.system?.cpu_temp ? `${status.system.cpu_temp.toFixed(1)}°C` : 'N/A'}
            icon={<Wifi className="w-6 h-6" />}
            status={status?.system?.cpu_temp && status.system.cpu_temp < 70 ? 'success' : 'warning'}
            description={
              status?.system?.memory_usage
                ? `Memory: ${status.system.memory_usage.toFixed(1)}%`
                : 'No data'
            }
          />

          <StatusCard
            title="Active Widgets"
            value={status?.widgets ? Object.keys(status.widgets).length : 0}
            icon={<Grid3x3 className="w-6 h-6" />}
            status="info"
            description="Running widgets"
          />
        </div>

        {/* Quick Actions */}
        <QuickActions onRefresh={fetchStatus} />

        {/* Widget Management */}
        <div className="mt-4">
          <WidgetList widgets={status?.widgets || {}} />
        </div>

        {/* System Information */}
        <div className="mt-4 p-6 bg-muted/50 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            System Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Device ID:</span>
              <span className="ml-2 font-medium">
                {status?.device_id || 'Unknown'}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Status:</span>
              <span className={`ml-2 font-medium ${status?.status === 'online' ? 'text-green-600' : 'text-red-600'}`}>
                {status?.status || 'Unknown'}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Uptime:</span>
              <span className="ml-2 font-medium">
                {status?.system?.uptime ? `${Math.floor(status.system.uptime / 60)} minutes` : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </SidebarInset>
  )
}
