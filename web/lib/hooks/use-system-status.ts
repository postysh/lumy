import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export function useSystemStatus() {
  return useQuery({
    queryKey: ['system-status'],
    queryFn: apiClient.getStatus,
    refetchInterval: 5000, // Refetch every 5 seconds
  })
}
