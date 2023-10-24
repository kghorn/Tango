import zmq
import time
import numpy as np
import gymnasium as gym

# observation, info = env.reset(seed=42)
# for _ in range(1000):
#     t0 = time.time()
#     action = env.action_space.sample()
#     observation, reward, terminated, truncated, info = env.step(action)

#     if terminated or truncated:
#         observation, info = env.reset()
#     times.append(time.time()-t0)
# env.close()

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8001")

print(f"Env server is ready on port 8001")

env = gym.make("CartPole-v1")

while True:
    
    message = socket.recv_json()
    #print(f"Received request: {message}")

    if message['type'] == 'action':
        observation, reward, terminated, truncated, info = env.step(int(message['action']))
        socket.send_json({
            'observation': observation.tolist(), 
            'reward': reward, 
            'terminated': terminated, 
            'truncated': truncated,
            'info': {}
        })

    if message['type'] == 'reset':
        observation, info = env.reset()
        socket.send_json({
            'observation': observation.tolist(),
            'info': {}
        })

    if message['type'] == 'close':
        socket.send_json({"info":"closed"})
        break

print("Done")