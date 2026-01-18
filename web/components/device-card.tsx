import { Monitor, Clock, Calendar, Activity, Thermometer, Cpu } from 'lucide-react'
import Link from 'next/link'

interface DeviceCardProps {
  device: {
    id: string
    device_id: string
    device_name: string
    is_online: boolean
    last_seen: string
    registered_at: string
    display_preview?: string
    current_status?: any
  }
}

export function DeviceCard({ device }: DeviceCardProps) {
  const isOnline = device.is_online && device.last_seen
  const lastSeen = device.last_seen ? new Date(device.last_seen) : null
  const registeredAt = device.registered_at ? new Date(device.registered_at) : null
  
  const timeSinceLastSeen = lastSeen
    ? Math.floor((Date.now() - lastSeen.getTime()) / 1000 / 60)
    : null

  const formatDate = (date: Date | null) => {
    if (!date) return 'N/A'
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const getUptimeText = () => {
    if (!timeSinceLastSeen) return 'N/A'
    if (timeSinceLastSeen < 1) return 'Just now'
    if (timeSinceLastSeen < 60) return `${timeSinceLastSeen}m ago`
    if (timeSinceLastSeen < 1440) return `${Math.floor(timeSinceLastSeen / 60)}h ago`
    return `${Math.floor(timeSinceLastSeen / 1440)}d ago`
  }

  return (
    <Link href={`/dashboard/devices/${device.device_id}`}>
      <div className="group relative overflow-hidden rounded-lg border bg-card p-6 hover:shadow-lg transition-all hover:border-primary cursor-pointer">
        {/* Status indicator */}
        <div className="absolute top-4 right-4 z-10">
          {isOnline ? (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <div className="h-2 w-2 rounded-full bg-green-600 animate-pulse" />
              <span className="text-xs font-medium">Online</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-2 w-2 rounded-full bg-muted-foreground" />
              <span className="text-xs">Offline</span>
            </div>
          )}
        </div>

        {/* Two-column layout: Preview on left, Info on right */}
        <div className="flex gap-4">
          {/* Left column: Display preview or icon */}
          <div className="flex-shrink-0">
            {device.display_preview ? (
              <div className="w-48 h-28 rounded-lg overflow-hidden border bg-muted">
                <img 
                  src={device.display_preview} 
                  alt="Current display" 
                  className="w-full h-full object-cover"
                />
              </div>
            ) : (
              <div className="w-48 h-28 flex items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                <Monitor className="h-8 w-8 text-primary" />
              </div>
            )}
          </div>

          {/* Right column: Device info */}
          <div className="flex-1 min-w-0">
            {/* Device name and ID */}
            <div className="space-y-0.5 mb-2">
              <h3 className="font-semibold text-sm truncate">{device.device_name}</h3>
              <p className="text-[10px] text-muted-foreground font-mono truncate">
                {device.device_id}
              </p>
            </div>

            {/* Device details grid */}
            <div className="space-y-1 text-[11px]">
              {/* Last seen */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Activity className="h-2.5 w-2.5 flex-shrink-0" />
                  <span>Last seen</span>
                </div>
                <span className="font-medium">{getUptimeText()}</span>
              </div>

              {/* Registered date */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Calendar className="h-2.5 w-2.5 flex-shrink-0" />
                  <span>Registered</span>
                </div>
                <span className="font-medium">{formatDate(registeredAt)}</span>
              </div>

              {/* System stats (if available) */}
              {device.current_status?.system && (
                <>
                  {device.current_status.system.cpu_temp && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Thermometer className="h-2.5 w-2.5 flex-shrink-0" />
                        <span>Temperature</span>
                      </div>
                      <span className="font-medium">
                        {device.current_status.system.cpu_temp.toFixed(1)}°C
                      </span>
                    </div>
                  )}
                  {device.current_status.system.memory_usage && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Cpu className="h-2.5 w-2.5 flex-shrink-0" />
                        <span>Memory</span>
                      </div>
                      <span className="font-medium">
                        {device.current_status.system.memory_usage.toFixed(0)}%
                      </span>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}
