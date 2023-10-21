## Tango Testing

Automated testing in this project includes both unit tests and integration tests. To live test full examples, see the project Makefile instead to launch example external environments and ML scripts.

The subfolders in the testing folder have the following purposes:

* **unit_tests/** - Tests for individual components, with all incoming and outgoing messages being mocked
* **integration_tests/** - Live testing of message routing using boilerplate "requester" and "responder" scripts. Profiling also occurs here
* **logs/** - "gateway", "requester", and "responder" scripts from integration testing will dump stdout and stderr into fles within this folder for easy test debugging