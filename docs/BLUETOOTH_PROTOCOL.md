# Lumy Bluetooth Protocol

This document describes the Bluetooth Low Energy (BLE) protocol used by Lumy for iPhone communication.

## Overview

Lumy uses BLE GATT (Generic Attribute Profile) for communication between the iPhone and Raspberry Pi. This provides low-power, reliable communication suitable for IoT devices.

## GATT Service

### Service UUID
```
12345678-1234-5678-1234-56789abcdef0
```

### Characteristics

#### TX Characteristic (Transmit from Pi)
- **UUID:** `12345678-1234-5678-1234-56789abcdef1`
- **Properties:** Notify, Read
- **Description:** Pi sends data to iPhone
- **Max Size:** 512 bytes

#### RX Characteristic (Receive on Pi)
- **UUID:** `12345678-1234-5678-1234-56789abcdef2`
- **Properties:** Write, Write Without Response
- **Description:** iPhone sends data to Pi
- **Max Size:** 512 bytes

## Message Format

All messages are JSON-formatted strings:

```json
{
  "command": "command_name",
  "data": {
    "key": "value"
  },
  "request_id": "unique_id"
}
```

### Fields

- **command** (required): The action to perform
- **data** (optional): Command-specific payload
- **request_id** (optional): Unique ID for request-response matching

## Commands

### 1. Ping
Check if device is responsive.

**Request:**
```json
{
  "command": "ping",
  "request_id": "123"
}
```

**Response:**
```json
{
  "command": "ping_response",
  "data": {
    "status": "pong",
    "timestamp": 1234567890.123
  },
  "request_id": "123"
}
```

### 2. Refresh Display
Trigger a full display refresh.

**Request:**
```json
{
  "command": "refresh_display",
  "request_id": "124"
}
```

**Response:**
```json
{
  "command": "refresh_display_response",
  "data": {
    "status": "success"
  },
  "request_id": "124"
}
```

### 3. Clear Display
Clear the E-Paper screen.

**Request:**
```json
{
  "command": "clear_display",
  "request_id": "125"
}
```

**Response:**
```json
{
  "command": "clear_display_response",
  "data": {
    "status": "success"
  },
  "request_id": "125"
}
```

### 4. Update Widget
Update data for a specific widget.

**Request:**
```json
{
  "command": "update_widget",
  "data": {
    "widget_id": "weather",
    "data": {
      "location": "San Francisco"
    }
  },
  "request_id": "126"
}
```

**Response:**
```json
{
  "command": "update_widget_response",
  "data": {
    "status": "success"
  },
  "request_id": "126"
}
```

### 5. Get Status
Get system status and widget information.

**Request:**
```json
{
  "command": "get_status",
  "request_id": "127"
}
```

**Response:**
```json
{
  "command": "get_status_response",
  "data": {
    "status": "online",
    "display_initialized": true,
    "widgets": {
      "clock": {
        "loaded": true,
        "last_update": 1234567890.123
      },
      "weather": {
        "loaded": true,
        "last_update": 1234567890.123
      }
    },
    "connected_clients": 1
  },
  "request_id": "127"
}
```

### 6. Set Configuration
Update system configuration.

**Request:**
```json
{
  "command": "set_config",
  "data": {
    "display.refresh_interval": 600,
    "widgets.weather.location": "New York"
  },
  "request_id": "128"
}
```

**Response:**
```json
{
  "command": "set_config_response",
  "data": {
    "status": "success"
  },
  "request_id": "128"
}
```

### 7. Trigger App
Trigger a specific widget/app action.

**Request:**
```json
{
  "command": "trigger_app",
  "data": {
    "app_name": "camera",
    "data": {
      "action": "take_photo"
    }
  },
  "request_id": "129"
}
```

**Response:**
```json
{
  "command": "trigger_app_response",
  "data": {
    "status": "success"
  },
  "request_id": "129"
}
```

## iOS Implementation Example

### Swift Code

```swift
import CoreBluetooth

class LumyBLEManager: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var centralManager: CBCentralManager!
    var lumyPeripheral: CBPeripheral?
    var txCharacteristic: CBCharacteristic?
    var rxCharacteristic: CBCharacteristic?
    
    let serviceUUID = CBUUID(string: "12345678-1234-5678-1234-56789abcdef0")
    let txUUID = CBUUID(string: "12345678-1234-5678-1234-56789abcdef1")
    let rxUUID = CBUUID(string: "12345678-1234-5678-1234-56789abcdef2")
    
    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }
    
    // MARK: - CBCentralManagerDelegate
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state == .poweredOn {
            centralManager.scanForPeripherals(
                withServices: [serviceUUID],
                options: nil
            )
        }
    }
    
    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String : Any],
        rssi RSSI: NSNumber
    ) {
        if peripheral.name == "Lumy Display" {
            lumyPeripheral = peripheral
            lumyPeripheral?.delegate = self
            centralManager.stopScan()
            centralManager.connect(peripheral, options: nil)
        }
    }
    
    func centralManager(
        _ central: CBCentralManager,
        didConnect peripheral: CBPeripheral
    ) {
        peripheral.discoverServices([serviceUUID])
    }
    
    // MARK: - CBPeripheralDelegate
    
    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverServices error: Error?
    ) {
        guard let services = peripheral.services else { return }
        
        for service in services {
            peripheral.discoverCharacteristics(
                [txUUID, rxUUID],
                for: service
            )
        }
    }
    
    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        guard let characteristics = service.characteristics else { return }
        
        for characteristic in characteristics {
            if characteristic.uuid == txUUID {
                txCharacteristic = characteristic
                peripheral.setNotifyValue(true, for: characteristic)
            } else if characteristic.uuid == rxUUID {
                rxCharacteristic = characteristic
            }
        }
    }
    
    func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateValueFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        guard let data = characteristic.value,
              let message = String(data: data, encoding: .utf8),
              let json = try? JSONSerialization.jsonObject(
                with: data,
                options: []
              ) as? [String: Any] else {
            return
        }
        
        // Handle received message
        handleMessage(json)
    }
    
    // MARK: - Commands
    
    func sendCommand(command: String, data: [String: Any]? = nil) {
        guard let rxChar = rxCharacteristic else { return }
        
        var message: [String: Any] = [
            "command": command,
            "request_id": UUID().uuidString
        ]
        
        if let data = data {
            message["data"] = data
        }
        
        guard let jsonData = try? JSONSerialization.data(
            withJSONObject: message,
            options: []
        ) else {
            return
        }
        
        lumyPeripheral?.writeValue(
            jsonData,
            for: rxChar,
            type: .withResponse
        )
    }
    
    func refreshDisplay() {
        sendCommand(command: "refresh_display")
    }
    
    func clearDisplay() {
        sendCommand(command: "clear_display")
    }
    
    func updateWeather(location: String) {
        sendCommand(
            command: "update_widget",
            data: [
                "widget_id": "weather",
                "data": ["location": location]
            ]
        )
    }
    
    private func handleMessage(_ json: [String: Any]) {
        // Handle response messages
        print("Received: \(json)")
    }
}
```

## Best Practices

1. **Always include request_id** for commands that expect responses
2. **Implement timeout handling** - wait max 5 seconds for response
3. **Handle disconnections gracefully** - reconnect automatically
4. **Batch updates** - avoid sending too many commands in quick succession
5. **Validate JSON** - check message structure before sending
6. **Handle errors** - check for "error" field in responses

## Error Handling

Errors are returned in this format:

```json
{
  "command": "error",
  "data": {
    "message": "Error description",
    "code": "ERROR_CODE"
  },
  "request_id": "original_request_id"
}
```

Common error codes:
- `INVALID_COMMAND`: Unknown command
- `INVALID_DATA`: Malformed or missing data
- `WIDGET_NOT_FOUND`: Specified widget doesn't exist
- `DISPLAY_ERROR`: Display operation failed
- `INTERNAL_ERROR`: Server-side error

## Security Considerations

1. **Pairing:** Require device pairing for initial connection
2. **Range:** BLE limited to ~10m range provides physical security
3. **Authentication:** Consider implementing custom auth layer for sensitive operations
4. **Encryption:** BLE provides built-in encryption for paired devices

## Future Enhancements

- [ ] Add authentication/authorization
- [ ] Support for file transfer (images)
- [ ] Batch command support
- [ ] Event subscriptions
- [ ] Over-the-air updates
