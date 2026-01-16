'use client'

import { useState } from 'react'
import { RefreshCw, Trash2, Zap } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface QuickActionsProps {
  onRefresh: () => void
}

export function QuickActions({ onRefresh }: QuickActionsProps) {
  const [loading, setLoading] = useState<string | null>(null)

  const handleAction = async (action: string, fn: () => Promise<any>) => {
    setLoading(action)
    try {
      await fn()
      onRefresh()
    } catch (error) {
      console.error(`Failed to ${action}:`, error)
      alert(`Failed to ${action}. Check console for details.`)
    } finally {
      setLoading(null)
    }
  }

  const actions = [
    {
      id: 'refresh',
      label: 'Auto-Refresh: 60s',
      icon: RefreshCw,
      onClick: () => alert('Display refreshes automatically every 60 seconds. Cloud commands coming soon!'),
      variant: 'primary' as const,
    },
    {
      id: 'status',
      label: 'Refresh Status',
      icon: RefreshCw,
      onClick: () => onRefresh(),
      variant: 'secondary' as const,
    },
  ]

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <Zap className="w-6 h-6 text-primary-500" />
        Quick Actions
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {actions.map((action) => {
          const Icon = action.icon
          const isLoading = loading === action.id
          
          const variants = {
            primary: 'bg-primary-500 hover:bg-primary-600 text-white',
            secondary: 'bg-gray-700 hover:bg-gray-600 text-white',
          }
          
          return (
            <button
              key={action.id}
              onClick={action.onClick}
              disabled={isLoading}
              className={`
                p-6 rounded-lg font-semibold transition-all duration-200
                flex items-center justify-center gap-3
                disabled:opacity-50 disabled:cursor-not-allowed
                ${variants[action.variant]}
                hover:shadow-lg hover:scale-105
              `}
            >
              <Icon className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              {action.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
