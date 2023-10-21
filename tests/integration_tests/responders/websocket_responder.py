 
import json
import time
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:8000/game/ws") as websocket:
        for _ in range(1000):
            message = json.loads(websocket.recv())
            print(f"Received: {message}")

            websocket.send(json.dumps({'msg':"World"}))
            print(f"Sending: World")

            #message = websocket.recv() # obligatory confirmation
            #print("Confirmed")

hello()