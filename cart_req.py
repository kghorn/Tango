
# import zmq
# import time
# import timeit

# from helper.profiling import print_profiling_stats

# def send_messages(socket):
    
#     print("Sending request...")
#     request = {'msg':"Hello"}
#     socket.send_json(request)

#     print("Waiting on reply...")
#     message = socket.recv_json()
#     print(f"Received reply {request} [ {message} ]")

# if __name__=="__main__":

#     total_messages = 1000

#     print("Connecting...")
#     context = zmq.Context()
#     socket = context.socket(zmq.REQ)
#     socket.connect("tcp://localhost:8001")

#     message_times = timeit.repeat(lambda: send_messages(socket),number=1,repeat=total_messages)
#     print_profiling_stats(message_times)

import gymnasium as gym
import tango_bindings
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import time

env = DummyVecEnv([lambda: gym.make("tango_bindings/ZeroMQ-v0")])
ModelClass = PPO

model = ModelClass("MlpPolicy", env, verbose=1)

message_times = []

obs = env.reset()
for step in range(100):
    #print('start',step)
    action, _ = model.predict(obs)
    t0 = time.time()
    obs, reward, done, info = env.step(action)
    message_times.append(time.time()-t0)
    #print('end',step)
env.close()
print('done')

rate = len(message_times) / sum(message_times)
print("")
print(f"Message rate:                {rate:,.0f} messages/second")
print(f"Message duration:            {1_000_000/rate:.2f} μs")
print(f"Mean chess games per second: {rate/40:,.0f} games (40 moves/game on average)")