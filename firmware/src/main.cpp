/**
 * Lumy Firmware v1.0.0
 * Test Program for ESP32-C6 1.47" LCD Display
 */

#include <Arduino.h>

// Pin definitions for Waveshare ESP32-C6 1.47" LCD
#define LCD_BL 3      // Backlight
#define LCD_RST 8     // Reset
#define LCD_DC 2      // Data/Command
#define LCD_CS 10     // Chip Select
#define LCD_SCLK 6    // SPI Clock
#define LCD_MOSI 7    // SPI MOSI

#define LCD_WIDTH 172
#define LCD_HEIGHT 320

void setup() {
    // Initialize Serial for debugging
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("====================================");
    Serial.println("Lumy Firmware v1.0.0");
    Serial.println("ESP32-C6 Test Program");
    Serial.println("====================================");
    
    // Initialize LCD backlight
    pinMode(LCD_BL, OUTPUT);
    digitalWrite(LCD_BL, HIGH);  // Turn on backlight
    
    Serial.println("✓ Backlight initialized");
    Serial.println("");
    Serial.println("Welcome to Lumy!");
    Serial.println("Board detected on: /dev/tty.usbmodem21101");
    Serial.println("");
    Serial.println("Next steps:");
    Serial.println("1. Install TFT_eSPI display library");
    Serial.println("2. Configure for ST7789 driver");
    Serial.println("3. Display 'Welcome to Lumy' on screen");
}

void loop() {
    // Blink LED to show it's running
    digitalWrite(LCD_BL, HIGH);
    delay(1000);
    digitalWrite(LCD_BL, LOW);
    delay(1000);
    
    static int counter = 0;
    Serial.printf("Running... %d seconds\n", ++counter);
}
