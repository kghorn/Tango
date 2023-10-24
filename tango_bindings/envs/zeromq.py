import json
import numpy as np
from gymnasium import Env
from gymnasium.core import ActType, ObsType
from gymnasium.spaces import Discrete, Box
from typing import Tuple
import zmq

import uuid

#TODO: verify all incoming websket data

class ZeroMQEnv(Env):

    socket = None

    def __init__(self, host: str='localhost', port: int=8001):

        #TODO: receive the action and observation spaces from the game itself
        # self.ws.send_json({'type':'init'})
        # msg = await self.ws.receive_json()

        # NOTE: Sokoban game
        # self.action_space = Discrete(4) # [up, right, down, left]
        # self.observation_space = Box(low=0,high=4,shape=(8,8),dtype='uint8') # [empty, wall, box, target, player]

        # NOTE: Cartpole example
        # self.action_space = Discrete(2)
        # theta_threshold_radians = 12 * 2 * np.pi / 360
        # x_threshold = 2.4
        # high = np.array([x_threshold * 2,np.finfo(np.float32).max,theta_threshold_radians * 2,np.finfo(np.float32).max],dtype=np.float32)
        # self.observation_space = Box(-high, high, dtype=np.float32) # [empty, wall, box, target, player]

        # NOTE: Empty env
        self.action_space = Discrete(2)
        obs_size = 4
        self.observation_space = Box(low=0, high=1, shape=(obs_size,), dtype='float32')

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{host}:{port}")

    def reset(self, **kwargs):

        # TODO: let's have a loop with a max number of tries, and confirm that rests are successful
        self.socket.send_json({'type':'reset',**kwargs})
        msg = self.socket.recv_json()


        # NOTE: Sokoban game
        # observation = np.array(msg['observation'],dtype='uint8') # TODO: resolve turning data['obbservation'] into an ObsType

        # NOTE: Cartpole example
        # observation = np.array(msg['observation'],dtype='float32') # TODO: resolve turning data['obbservation'] into an ObsType

        # NOTE: Empty env
        observation = np.array(msg['observation'],dtype='float32') # TODO: resolve turning data['obbservation'] into an ObsType
        # msg_arr = self.socket.recv()
        # observation = np.frombuffer(memoryview(msg_arr),dtype='float32')

        return observation, msg['info']

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, bool, dict]:

        self.socket.send_json({'type':'action','action':str(action)})
        msg = self.socket.recv_json()

        # NOTE: Sokoban game
        # observation = np.array(msg['observation'],dtype='uint8') # TODO: resolve turning data['obbservation'] into an ObsType

        # NOTE: Cartpole example
        # observation = np.array(msg['observation'],dtype='float32') # TODO: resolve turning data['obbservation'] into an ObsType

        # NOTE: Empty env
        observation = np.array(msg['observation'],dtype='float32') # TODO: resolve turning data['obbservation'] into an ObsType
        # msg_arr = self.socket.recv()
        # observation = np.frombuffer(memoryview(msg_arr),dtype='float32')

        reward, terminated, truncated = float(msg['reward']), bool(msg['terminated']), bool(msg['truncated'])

        return observation, reward, terminated, truncated, msg['info']

    def close(self):

        self.socket.send_json({'type':'close'})
        msg = self.socket.recv_json()

        return msg

    def __del__(self):

        if self.socket is not None:
            self.socket.close()
            self.socket = None