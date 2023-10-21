 
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8001")

while True:
    #  Wait for next request from client
    message = socket.recv_json()
    print(f"Received request: {message}")

    #  Send reply back to client
    socket.send_json({'msg':"World"})