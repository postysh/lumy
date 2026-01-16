'use client'

import { Grid3x3, Clock, CloudSun, Calendar } from 'lucide-react'

interface WidgetListProps {
  widgets: Record<string, any>
}

const widgetIcons: Record<string, any> = {
  clock: Clock,
  weather: CloudSun,
  calendar: Calendar,
}

export function WidgetList({ widgets }: WidgetListProps) {
  const widgetEntries = Object.entries(widgets)

  if (widgetEntries.length === 0) {
    return (
      <div className="p-8 bg-gray-800/50 rounded-lg border border-gray-700 text-center">
        <Grid3x3 className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400">No widgets loaded</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <Grid3x3 className="w-6 h-6 text-primary-500" />
        Active Widgets
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {widgetEntries.map(([name, widget]) => {
          const Icon = widgetIcons[name] || Grid3x3
          
          return (
            <div
              key={name}
              className="p-6 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-primary-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-primary-500/10"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-primary-500/10 rounded-lg">
                  <Icon className="w-5 h-5 text-primary-500" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white capitalize">
                    {name}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {widget.loaded ? 'Active' : 'Inactive'}
                  </p>
                </div>
              </div>
              
              {widget.last_update && (
                <p className="text-sm text-gray-400">
                  Last update: {new Date(widget.last_update * 1000).toLocaleTimeString()}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
