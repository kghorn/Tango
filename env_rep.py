import zmq
import time
import numpy as np
import gymnasium as gym

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8001")

print(f"Env server is ready on port 8001")

class EmptyEnv(gym.Env):
    def __init__(self, obs_size: int = 4):
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(obs_size,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(2)
        self.zeros = np.zeros(obs_size, dtype=np.float32)

    def reset(self, seed: int | None = None, options: dict | None = None):
        return self.zeros, {}

    def step(self, action):
        return self.zeros, 0, False, False, {}

env = EmptyEnv()

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
        })#,flags=zmq.SNDMORE)
        #socket.send(observation)


    if message['type'] == 'reset':
        observation, info = env.reset()
        socket.send_json({
            'observation': observation.tolist(),
            'info': {}
        })#,flags=zmq.SNDMORE)
        #socket.send(observation)

    if message['type'] == 'close':
        socket.send_json({"info":"closed"})
        break

print("Done")