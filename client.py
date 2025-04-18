import socket
import json
import pyautogui
from pynput.mouse import Button
import sys
import platform

class Client:
    def __init__(self, host, port=5000):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.is_linux = platform.system().lower() == 'linux'
        # Adjust margin based on platform
        self.margin = 5 if self.is_linux else 10
        # Disable PyAutoGUI failsafe on Linux
        if self.is_linux:
            pyautogui.FAILSAFE = False

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
                
                # Handle edge transition
                if command.get('is_edge', False):
                    # When at the edge, move to the right edge of client screen
                    x = self.screen_width - self.margin
                    if self.is_linux:
                        pyautogui.moveTo(x, y)
                    else:
                        pyautogui.moveTo(x, y, duration=0.1)
                else:
                    # For normal mouse movements, map the coordinates to client screen
                    # Calculate the relative position on the client screen
                    server_width = command.get('server_width', self.screen_width)
                    server_height = command.get('server_height', self.screen_height)
                    
                    # Map x coordinate from server to client screen
                    relative_x = (x - self.margin) / (server_width - 2 * self.margin)
                    mapped_x = int(relative_x * (self.screen_width - 2 * self.margin) + self.margin)
                    
                    # Map y coordinate from server to client screen
                    relative_y = y / server_height
                    mapped_y = int(relative_y * self.screen_height)
                    
                    # Ensure coordinates stay within screen bounds
                    mapped_x = max(self.margin, min(mapped_x, self.screen_width - self.margin))
                    mapped_y = max(0, min(mapped_y, self.screen_height))
                    
                    if self.is_linux:
                        pyautogui.moveTo(mapped_x, mapped_y)
                    else:
                        pyautogui.moveTo(mapped_x, mapped_y, duration=0.1)
            
            elif command['type'] == 'mouse_click':
                x = command['x']
                y = command['y']
                button_str = command['button']
                pressed = command['pressed']
                
                # Convert string button to Button enum
                if 'Button.left' in button_str:
                    button = Button.left
                elif 'Button.right' in button_str:
                    button = Button.right
                elif 'Button.middle' in button_str:
                    button = Button.middle
                else:
                    button = Button.left  # Default to left button if unknown
                
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