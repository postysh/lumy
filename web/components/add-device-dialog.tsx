'use client'

import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'

interface AddDeviceDialogProps {
  onDeviceAdded?: () => void
}

export function AddDeviceDialog({ onDeviceAdded }: AddDeviceDialogProps) {
  const [open, setOpen] = useState(false)
  const [code, setCode] = useState('')
  const [deviceName, setDeviceName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/devices/claim', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code.toUpperCase().trim(),
          device_name: deviceName || 'Lumy Display',
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to claim device')
      }

      // Success!
      setOpen(false)
      setCode('')
      setDeviceName('')
      if (onDeviceAdded) {
        onDeviceAdded()
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="lg" className="gap-2">
          <Plus className="w-5 h-5" />
          Add Device
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add Lumy Device</DialogTitle>
            <DialogDescription>
              Enter the 6-character code shown on your Lumy display to register it to your account.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {error && (
              <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
            <div className="grid gap-2">
              <label htmlFor="code" className="text-sm font-medium">
                Registration Code
              </label>
              <Input
                id="code"
                placeholder="ABC-123"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                required
                disabled={loading}
                maxLength={7}
                className="text-lg tracking-wider font-mono"
              />
              <p className="text-xs text-muted-foreground">
                Format: ABC-123 (3 letters, dash, 3 numbers)
              </p>
            </div>
            <div className="grid gap-2">
              <label htmlFor="name" className="text-sm font-medium">
                Device Name (Optional)
              </label>
              <Input
                id="name"
                placeholder="Lumy Display"
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Claiming...' : 'Add Device'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
