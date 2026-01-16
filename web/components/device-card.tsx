import { Monitor, Wifi, WifiOff, Clock } from 'lucide-react'
import Link from 'next/link'

interface DeviceCardProps {
  device: {
    id: string
    device_id: string
    device_name: string
    is_online: boolean
    last_seen: string
    current_status?: any
  }
}

export function DeviceCard({ device }: DeviceCardProps) {
  const isOnline = device.is_online && device.last_seen
  const lastSeen = device.last_seen ? new Date(device.last_seen) : null
  const timeSinceLastSeen = lastSeen
    ? Math.floor((Date.now() - lastSeen.getTime()) / 1000 / 60)
    : null

  return (
    <Link href={`/dashboard/devices/${device.device_id}`}>
      <div className="group relative overflow-hidden rounded-lg border bg-card p-6 hover:shadow-lg transition-all hover:border-primary cursor-pointer">
        {/* Status indicator */}
        <div className="absolute top-4 right-4">
          {isOnline ? (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <div className="h-2 w-2 rounded-full bg-green-600 animate-pulse" />
              <span className="text-xs">Online</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-2 w-2 rounded-full bg-muted-foreground" />
              <span className="text-xs">Offline</span>
            </div>
          )}
        </div>

        {/* Device icon */}
        <div className="mb-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
            <Monitor className="h-6 w-6 text-primary" />
          </div>
        </div>

        {/* Device info */}
        <div className="space-y-2">
          <h3 className="font-semibold text-lg">{device.device_name}</h3>
          <p className="text-sm text-muted-foreground font-mono">
            {device.device_id}
          </p>
          
          {/* Last seen */}
          {timeSinceLastSeen !== null && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2">
              <Clock className="h-3 w-3" />
              {timeSinceLastSeen < 1
                ? 'Just now'
                : timeSinceLastSeen < 60
                ? `${timeSinceLastSeen}m ago`
                : `${Math.floor(timeSinceLastSeen / 60)}h ago`}
            </div>
          )}
        </div>

        {/* System stats (if available) */}
        {device.current_status?.system && (
          <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-2 text-xs">
            {device.current_status.system.cpu_temp && (
              <div>
                <span className="text-muted-foreground">CPU:</span>
                <span className="ml-1 font-medium">
                  {device.current_status.system.cpu_temp.toFixed(1)}°C
                </span>
              </div>
            )}
            {device.current_status.system.memory_usage && (
              <div>
                <span className="text-muted-foreground">RAM:</span>
                <span className="ml-1 font-medium">
                  {device.current_status.system.memory_usage.toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </Link>
  )
}
