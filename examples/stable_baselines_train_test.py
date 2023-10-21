import gymnasium as gym
import tango_bindings
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import time

env = DummyVecEnv([lambda: gym.make("tango_bindings/ZeroMQ-v0")])
ModelClass = PPO

model = ModelClass("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)
model.save("examples/phaser/sokoban/stable_baselines_test_ppo_level1")

obs = env.reset()
while True
    action, _ = model.predict(obs)
    obs, reward, done, info = env.step(action)
    if reward>=100.:
        break
    time.sleep(.1)
env.close()
