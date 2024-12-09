OS = $(shell echo $$OS)
ifeq ($(OS),Windows_NT)
	SUDO =
else
	SUDO = sudo
endif

venv:
	python3 -m venv venv

install: venv requirements.txt
	./venv/bin/pip3 install -r requirements.txt

.PHONY: run-node
run-node: venv install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node 127.0.0.1:30000

run-node-test-1: venv install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node1 127.0.0.1:30001

run-node-test-2: venv install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node2 127.0.0.1:30002

run-node-test-3: venv install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node3 127.0.0.1:30003

run-node-test-4: venv install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node4 127.0.0.1:30004

run-node-test-5: venv install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node5 127.0.0.1:30005

clean:
	rm -rf venv
	rm -rf __pycache__
