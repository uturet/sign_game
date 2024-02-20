import websocket
import rel
from websocket import create_connection
import random
import sys

HOST = 'localhost'
PORT = int(sys.argv[1])

def on_message(ws, message):
    print("MESSAGE:", message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    ws.send(f"Hello, World {random.randint(0, 10000)}")


def start():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://{HOST}:{PORT}/room",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel,
                   reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()


def connect():
    ws = create_connection(f"ws://{HOST}:{PORT}")
    print(ws.recv())
    print("Sending 'Hello, World'...")
    ws.send("Hello, World")
    print("Sent")
    print("Receiving...")
    result = ws.recv()
    print("Received '%s'" % result)
    ws.close()


if __name__ == "__main__":
    start()
    # connect()
