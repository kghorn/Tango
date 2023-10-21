import io
import subprocess
import time
import unittest

class TestZMQToWebSocketRoundtrip(unittest.TestCase):

    def setUp(self):

        self.gateway_process = self.run_script_with_logging(['python','-m','sanic','gateways.zmq_to_websocket_gateway.app','--host=localhost','--port=8000','--workers=1'], 'zmq_to_websocket_gateway')
        time.sleep(0.5) # TODO: better server readiness management
        
        self.responder_process = self.run_script_with_logging(['python','./tests/integration_tests/responders/websocket_responder.py'], 'zmq_to_websocket_responder')
        time.sleep(0.5) # TODO: better server readiness management

    def test_send_1000_messages(self):
        
        self.requester_process = self.run_script_with_logging(['python','./tests/integration_tests/requesters/zmq_requester.py'], 'zmq_to_websocket_requester')
        assert(self.requester_process.wait()==0)

    def run_script_with_logging(self, script_command: list[str], logging_filename):

        with io.open(f'./tests/logs/{logging_filename}.txt','w') as out:
            process = subprocess.Popen(['timeout','10']+script_command,stdout=out,stderr=subprocess.STDOUT)
        return process

    def tearDown(self):

        self.responder_process.terminate()
        self.responder_process.wait()
        self.gateway_process.terminate()
        self.gateway_process.wait()