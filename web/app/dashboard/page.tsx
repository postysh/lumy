'use client'

import { useEffect, useState } from 'react'
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
import { EmptyState } from '@/components/empty-state'
import { AddDeviceDialog } from '@/components/add-device-dialog'
import { DeviceCard } from '@/components/device-card'

export default function DashboardPage() {
  const [devices, setDevices] = useState<any[]>([])
  const [loadingDevices, setLoadingDevices] = useState(true)

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices')
      if (response.ok) {
        const data = await response.json()
        setDevices(data)
      }
    } catch (error) {
      console.error('Failed to fetch devices:', error)
    } finally {
      setLoadingDevices(false)
    }
  }

  useEffect(() => {
    fetchDevices()
    
    // Poll for device status updates every 5 seconds
    const intervalId = setInterval(() => {
      fetchDevices()
    }, 5000)
    
    return () => clearInterval(intervalId)
  }, [])

  const handleDeviceAdded = () => {
    fetchDevices()
  }

  // Show loading state
  if (loadingDevices) {
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
        <div className="flex flex-1 items-center justify-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </SidebarInset>
    )
  }

  // Show empty state if no devices
  if (devices.length === 0) {
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
        <EmptyState onDeviceAdded={handleDeviceAdded} />
      </SidebarInset>
    )
  }

  // Show dashboard with device grid
  return (
    <SidebarInset>
      <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>My Devices</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <div className="ml-auto">
          <AddDeviceDialog onDeviceAdded={handleDeviceAdded} />
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-4 p-6">
        {/* Page title */}
        <div>
          <h2 className="text-2xl font-bold">Your Devices</h2>
          <p className="text-muted-foreground">
            Manage and monitor your Lumy displays
          </p>
        </div>

        {/* Device grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {devices.map((device) => (
            <DeviceCard key={device.id} device={device} />
          ))}
        </div>
      </div>
    </SidebarInset>
  )
}
