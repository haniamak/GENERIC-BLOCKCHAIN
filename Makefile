OS = $(shell echo $$OS)
ifeq ($(OS),Windows_NT)
	SUDO =
else
	SUDO = sudo
endif

venv:
	python -m venv venv

install: venv requirements.txt
	./venv/bin/pip install -r requirements.txt

.PHONY: run-node
run-node:
	$(SUDO) ./venv/bin/python ./node/node.py

clean:
	rm -rf venv
	rm -rf __pycache__
