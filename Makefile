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
	$(SUDO) ./venv/bin/python3 ./node/node.py

clean:
	rm -rf venv
	rm -rf __pycache__
