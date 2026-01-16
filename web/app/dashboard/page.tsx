'use client'

import { Monitor, Wifi, Grid3x3, Settings } from 'lucide-react'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { StatusCard } from '@/components/status-card'
import { WidgetList } from '@/components/widget-list'
import { QuickActions } from '@/components/quick-actions'
import { useSystemStatus } from '@/lib/hooks/use-system-status'

export default function DashboardPage() {
  const { data: status, isLoading, refetch } = useSystemStatus()

  return (
    <SidebarInset>
      <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Dashboard</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <div className="flex flex-1 flex-col gap-4 p-6">
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
        <QuickActions onRefresh={refetch} />

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
