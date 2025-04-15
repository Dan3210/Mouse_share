import socket
import json
import pyautogui
from pynput import mouse, keyboard
import threading
import sys
import platform

class Server:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.running = False
        self.is_linux = platform.system().lower() == 'linux'
        # Adjust margin based on platform
        self.margin = 5 if self.is_linux else 10

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        # Start mouse and keyboard listeners
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            while True:
                print("Waiting for client connection...")
                self.client_socket, self.client_address = self.server_socket.accept()
                print(f"Client connected from {self.client_address}")
                self.running = True
                self.handle_client()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.cleanup()

    def handle_client(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                # Handle any incoming data from client if needed
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.running = False
            if self.client_socket:
                self.client_socket.close()

    def on_mouse_move(self, x, y):
        if not self.running:
            return

        # Send all mouse movements, not just edge transitions
        data = {
            'type': 'mouse_move',
            'x': x,
            'y': y,
            'platform': 'linux' if self.is_linux else 'windows',
            'server_width': self.screen_width,
            'server_height': self.screen_height,
            'is_edge': x <= self.margin  # Flag to indicate if this is an edge transition
        }
        self.send_data(data)

    def on_mouse_click(self, x, y, button, pressed):
        if not self.running:
            return

        data = {
            'type': 'mouse_click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'platform': 'linux' if self.is_linux else 'windows'
        }
        self.send_data(data)

    def on_key_press(self, key):
        if not self.running:
            return

        try:
            data = {
                'type': 'key_press',
                'key': str(key),
                'platform': 'linux' if self.is_linux else 'windows'
            }
            self.send_data(data)
        except AttributeError:
            pass

    def on_key_release(self, key):
        if not self.running:
            return

        try:
            data = {
                'type': 'key_release',
                'key': str(key),
                'platform': 'linux' if self.is_linux else 'windows'
            }
            self.send_data(data)
        except AttributeError:
            pass

    def send_data(self, data):
        if self.client_socket:
            try:
                self.client_socket.send((json.dumps(data) + '\n').encode())
            except Exception as e:
                print(f"Error sending data: {e}")
                self.running = False

    def cleanup(self):
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

if __name__ == "__main__":
    server = Server()
    server.start()