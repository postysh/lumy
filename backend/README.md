# Lumy Backend

Backend service for Lumy e-paper display devices.

## Configuration

Set these environment variables (or create a `.env` file):

- `LUMY_API_URL`: Your Vercel dashboard URL (e.g., `https://your-app.vercel.app`)
- `LUMY_API_KEY`: API key for device authentication (must match the key in your Vercel environment variables)

## Files

- `main.py`: Main application entry point
- `display_manager.py`: Handles e-paper display operations
- `api_client.py`: Communicates with the Lumy dashboard API
- `device_manager.py`: Manages device ID and state
- `config.py`: Configuration settings

## How It Works

1. Device generates a unique device ID (from MAC address)
2. Device generates a random 6-character registration code
3. Device registers with the dashboard API
4. Device displays the welcome screen with the registration code
5. User visits the dashboard and enters the code to claim the device
6. Device polls the API to check if it's been claimed
7. Once claimed, device fetches and displays configured widgets
8. Device sends periodic heartbeats and refreshes configuration

## Installation

See the main README.md for installation instructions.
