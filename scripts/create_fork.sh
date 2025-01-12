#!/bin/bash

# first block
./scripts/sendFile.sh 1
./scripts/sendFile.sh 1
./scripts/sendFile.sh 1

echo "First block sent"
sleep 5

# block a and b
./scripts/sendFile.sh 2
./scripts/sendFile.sh 1
./scripts/sendFile.sh 2
./scripts/sendFile.sh 1
./scripts/sendFile.sh 2
./scripts/sendFile.sh 1

echo "Block a and b sent"