import { Monitor } from 'lucide-react'
import { AddDeviceDialog } from './add-device-dialog'

interface EmptyStateProps {
  onDeviceAdded?: () => void
}

export function EmptyState({ onDeviceAdded }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-8">
      <div className="max-w-md text-center space-y-6">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="rounded-full bg-muted p-6">
            <Monitor className="w-16 h-16 text-muted-foreground" />
          </div>
        </div>

        {/* Heading */}
        <div className="space-y-2">
          <h2 className="text-2xl font-bold">No Devices Yet</h2>
          <p className="text-muted-foreground">
            Get started by adding your first Lumy display. Power on your device and enter the registration code shown on the screen.
          </p>
        </div>

        {/* CTA */}
        <AddDeviceDialog onDeviceAdded={onDeviceAdded} />

        {/* Help text */}
        <div className="pt-4 space-y-2 text-sm text-muted-foreground">
          <p className="font-medium">Need help?</p>
          <ol className="text-left space-y-1 list-decimal list-inside">
            <li>Power on your Raspberry Pi with Lumy installed</li>
            <li>Wait for the display to show a 6-character code</li>
            <li>Click &quot;Add Device&quot; and enter the code</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
