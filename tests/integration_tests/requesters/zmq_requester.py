
import zmq
import time
import timeit

from helper.profiling import print_profiling_stats

def send_messages(socket):
    
    print("Sending request...")
    request = {'msg':"Hello"}
    socket.send_json(request)

    print("Waiting on reply...")
    message = socket.recv_json()
    print(f"Received reply {request} [ {message} ]")

if __name__=="__main__":

    total_messages = 1000

    print("Connecting...")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:8001")

    message_times = timeit.repeat(lambda: send_messages(socket),number=1,repeat=total_messages)
    print_profiling_stats(message_times)
