OS = $(shell echo $$OS)
ifeq ($(OS),Windows_NT)
	SUDO =
else
	SUDO =
endif

venv:
	python3 -m venv venv

# install: venv requirements.txt
# 	# ./venv/bin/pip3 install -r requirements.txt

.PHONY: run-node
run-node: venv # install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node 127.0.0.1:30000 --temporary

run-node-test-1: venv # install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node1 127.0.0.1:30001 --temporary

run-node-test-2: venv # install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node2 127.0.0.1:30002 --temporary

run-node-test-3: venv # install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node3 127.0.0.1:30003 --temporary

run-node-test-4: venv # install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node4 127.0.0.1:30004 --temporary

run-node-test-5: venv # install
	$(SUDO) ./venv/bin/python3 ./node/node.py ./node-test/node5 127.0.0.1:30005 --temporary

clean:
	rm -rf venv
	rm -rf __pycache__
