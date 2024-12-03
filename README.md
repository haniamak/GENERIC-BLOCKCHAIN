# GENERIC-BLOCKCHAIN

### **How to run**
This will not work on Windows, because Windows dosen't support pysctp.

Make sure you have installed these packages:
`sudo apt install libsctp-dev python3-dev build-essential autoconf`

First, create the python virtual environment with:

`make venv`

then, install requirements with:

`make install`

to start the node:

`make run-node`
