# Laptop Sync

A Python-based solution for syncing two laptops, allowing one laptop to control another's mouse and keyboard. When the mouse reaches the edge of one screen, it seamlessly transitions to the other screen.

## Features

- Mouse control synchronization
- Keyboard control synchronization
- Seamless screen edge transition
- Simple setup and usage

## Requirements

- Python 3.6 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - pyautogui
  - pynput
  - pillow

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### On the Server Laptop (The one controlling the other laptop)

1. Run the server:
   ```bash
   python server.py
   ```
2. The server will start listening for connections on port 5000

### On the Client Laptop (The one being controlled)

1. Run the client with the server's IP address:
   ```bash
   python client.py <server_ip>
   ```
   Replace `<server_ip>` with the actual IP address of the server laptop

## How it Works

1. The server laptop captures mouse and keyboard events
2. When the mouse reaches the edge of the screen, the control is transferred to the client laptop
3. The client laptop receives and executes the mouse and keyboard commands
4. The transition between screens is seamless when moving the mouse to the edges

## Security Note

This software does not include any encryption. It is recommended to use this only on trusted networks. For secure usage, consider setting up a VPN between the two laptops.

## Troubleshooting

1. Make sure both laptops are on the same network
2. Check if port 5000 is not blocked by the firewall
3. Verify that the server IP address is correct when connecting from the client
4. Ensure all required packages are installed on both laptops

## Limitations

- Currently supports only one client connection
- No encryption (use on trusted networks only)
- May require administrative privileges on some systems