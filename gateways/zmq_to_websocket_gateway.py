import json

import zmq
from zmq.asyncio import Context

from sanic import Sanic, Request, Websocket
from sanic.response import text

app = Sanic("TestBridgeApp")

@app.before_server_start
async def setup_zmq(app, _):
    
    context = Context.instance()
    app.ctx.zmq = context.socket(zmq.REP)
    app.ctx.zmq.bind('tcp://127.0.0.1:8001') #TODO: multiple workers cause port collisions
    app.add_task(zeromq_to_ws(app))

async def zeromq_to_ws(app):

    print('zmq ready')
    while True:
        msg = await app.ctx.zmq.recv_json()
        print(f'ZeroMQ received Internal: {msg}')
        await app.ctx.ws.send(json.dumps(msg))
        print(f'ZeroMQ sent to External: {msg}')
    print('zmq closed')

@app.websocket("/game/ws")
async def ws_to_zeromq(request, ws):
    print(request)
    app.ctx.ws = ws
    print('ws ready')
    while True:
        print('ingesting ws')
        msg = json.loads(await app.ctx.ws.recv())
        print(f'WS received External: {msg}')
        #await app.ctx.ws.send(json.dumps({'msg':"Confirmed"})) #TODO: TCP_NODELAY to disable Nagle's algorithm w/ a comment in the readme (https://saturncloud.io/blog/the-tcpnodelay-option-should-you-turn-off-nagles-algorithm/)

        await app.ctx.zmq.send_json(msg)
        print(f'WS sent to Internal: {msg}')
    
    print('ws disconnected')

#python -m sanic zmq_to_websocket_gateway.app --host=localhost --port=8000 --workers=1
#uvicorn myapp:app