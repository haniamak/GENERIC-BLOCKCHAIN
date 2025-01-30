# GENERIC-BLOCKCHAIN

## Project Overview
This project implements a generic blockchain system with peer-to-peer communication between nodes. It includes features such as block creation, entry (transaction) management, and node synchronization.

## Requirements
Before running the project, ensure the following packages are installed on your system:

```sh
sudo apt install python3-dev build-essential autoconf
```

Additionally, Python 3 is required.

## Installation

1. **Clone the repository**:
```sh
git clone https://github.com/haniamak/GENERIC-BLOCKCHAIN.git
cd GENERIC-BLOCKCHAIN
```

2. **Set up a Python virtual environment**:
```sh
make venv
```

3. **Install dependencies**:
```sh
make install
```

## How to Run Nodes
The Makefile allows you to run multiple test nodes. Each node listens on a unique address and port.
```sh
make run-node-test-1   # Runs node on 127.0.0.1:30001
make run-node-test-2   # Runs node on 127.0.0.1:30002
make run-node-test-3   # Runs node on 127.0.0.1:30003
make run-node-test-4   # Runs node on 127.0.0.1:30004
make run-node-test-5   # Runs node on 127.0.0.1:30005
```
Each node temporarily stores entries and synchronizes blocks with other nodes.

## Clean Up
To remove the virtual environment and pycache, run:
```sh
make clean
```
