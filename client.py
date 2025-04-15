import socket
import json
import pyautogui
from pynput.mouse import Button
import sys

class Client:
    def __init__(self, host, port=5000):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = False
        self.screen_width, self.screen_height = pyautogui.size()

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            self.running = True
            self.receive_commands()
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.cleanup()

    def receive_commands(self):
        buffer = ""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                buffer += data.decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        command = json.loads(line)
                        self.execute_command(command)
            except Exception as e:
                print(f"Error receiving command: {e}")
                break

    def execute_command(self, command):
        try:
            if command['type'] == 'mouse_move':
                x = command['x']
                y = command['y']
                
                # Handle transition from server to client
                margin = 10
                if x <= margin:
                    # When receiving a transition command (x <= margin),
                    # move the cursor to the right edge of client screen
                    x = self.screen_width - margin
                    pyautogui.moveTo(x, y, duration=0.1)
                else:
                    # For normal mouse movements, use the received coordinates directly
                    # This allows free movement on the client screen
                    pyautogui.moveTo(x, y, duration=0.1)
            
            elif command['type'] == 'mouse_click':
                x = command['x']
                y = command['y']
                button = command['button']
                pressed = command['pressed']
                
                # Convert string button to Button enum
                if 'left' in button.lower():
                    button = Button.left
                elif 'right' in button.lower():
                    button = Button.right
                elif 'middle' in button.lower():
                    button = Button.middle
                
                if pressed:
                    pyautogui.mouseDown(x, y, button=button)
                else:
                    pyautogui.mouseUp(x, y, button=button)
            
            elif command['type'] in ['key_press', 'key_release']:
                key = command['key']
                # Remove quotes from key string
                key = key.strip("'")
                
                if command['type'] == 'key_press':
                    pyautogui.keyDown(key)
                else:
                    pyautogui.keyUp(key)
        
        except Exception as e:
            print(f"Error executing command: {e}")

    def cleanup(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <server_ip>")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    client = Client(server_ip)
    client.connect()