from gymnasium.envs.registration import register

register(
    id='tango_bindings/WebSocket-v0',
    entry_point='tango_bindings.envs:WebSocketEnv'
)

register(
    id='tango_bindings/HTTP-v0',
    entry_point='tango_bindings.envs:HTTPEnv'
)

register(
    id='tango_bindings/ZeroMQ-v0',
    entry_point='tango_bindings.envs:ZeroMQEnv'
)