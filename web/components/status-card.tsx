import { ReactNode } from 'react'

interface StatusCardProps {
  title: string
  value: string | number
  icon: ReactNode
  status?: 'success' | 'error' | 'warning' | 'info'
  description?: string
}

export function StatusCard({ 
  title, 
  value, 
  icon, 
  status = 'info',
  description 
}: StatusCardProps) {
  const statusColors = {
    success: 'text-green-500 bg-green-500/10 border-green-500/20',
    error: 'text-red-500 bg-red-500/10 border-red-500/20',
    warning: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
    info: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  }

  return (
    <div className={`p-6 rounded-lg border backdrop-blur-sm ${statusColors[status]}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-300">{title}</h3>
        <div className={`p-2 rounded-lg ${statusColors[status]}`}>
          {icon}
        </div>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-white">{value}</p>
        {description && (
          <p className="text-sm text-gray-400">{description}</p>
        )}
      </div>
    </div>
  )
}
