import io
import os
import subprocess
import unittest

class TestZMQToZMQRoundtrip(unittest.TestCase):

    def setUp(self):

        self.responder_process = self.run_script_with_logging(['python','./tests/integration_tests/responders/zmq_responder.py'], 'zmq_to_zmq_responder')

    def test_send_1000_messages(self):

        self.requester_process = self.run_script_with_logging(['python','./tests/integration_tests/requesters/zmq_requester.py'], 'zmq_to_zmq_requester')
        assert(self.requester_process.wait()==0)

    def run_script_with_logging(self, script_command: list[str], logging_filename):

        with io.open(f'./tests/logs/{logging_filename}.txt','w') as out:
            process = subprocess.Popen(['timeout','10']+script_command,stdout=out,stderr=subprocess.STDOUT,env=os.environ)
        return process

    def tearDown(self):

        self.responder_process.terminate()
        self.responder_process.wait()

            
# zmq to zmq
# Final wall time: 31,143.66331046363 messages/second
# Mean message time: 31.899213790893555 µs
# Chess games per second (40 moves on average): 783.72

# zmq to zmq (w/o print statements):
# Final wall time: 32,170.088741285024 messages/second
# Mean message time: 30.896425247192383 µs
# Chess games per second (40 moves on average): 809.16

# zmq to websockets
# Final wall time: 7,034.035623785191 messages/second
# Mean message time: 141.91102981567383 µs
# Chess games per second (40 moves on average): 176.17

# def x():
#     t0 = time.time()
#     for _ in range(1000):
#         json.loads(json.dumps(payload))
#     return time.time()-t0
# Final wall time: 125,221.79429765638 messages/second
# Mean message time: 7.395267486572266 µs