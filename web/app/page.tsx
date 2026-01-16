'use client'

import { useEffect, useState } from 'react'
import { Monitor, Wifi, RefreshCw, Settings, Grid3x3 } from 'lucide-react'
import { StatusCard } from '@/components/status-card'
import { WidgetList } from '@/components/widget-list'
import { QuickActions } from '@/components/quick-actions'
import { useSystemStatus } from '@/lib/hooks/use-system-status'

export default function Home() {
  const { data: status, isLoading, refetch } = useSystemStatus()

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Monitor className="w-10 h-10 text-primary-500" />
            Lumy Dashboard
          </h1>
          <p className="text-gray-400">
            Control your E-Paper display from anywhere
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
        <div className="mt-8">
          <WidgetList widgets={status?.widgets || {}} />
        </div>

        {/* Connection Info */}
        <div className="mt-8 p-6 bg-gray-800/50 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            System Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Device ID:</span>
              <span className="text-white ml-2 font-medium">
                {status?.device_id || 'Unknown'}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Status:</span>
              <span className={`ml-2 font-medium ${status?.status === 'online' ? 'text-green-400' : 'text-red-400'}`}>
                {status?.status || 'Unknown'}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Uptime:</span>
              <span className="text-white ml-2 font-medium">
                {status?.system?.uptime ? `${Math.floor(status.system.uptime / 60)} minutes` : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
