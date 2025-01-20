#!/bin/bash
echo "Usage: ./testLoop.sh <nodenum>"
nodenum=$1

# while true
# for i in {1..nodenum}
# do
#     # Generate 64 random characters and save to a file
#     ./scripts/sendFile $i
#     sleep 1
# done
while true; do
    for i in $(seq $nodenum); do
        echo "Sending file to node $i"
        sudo ./scripts/sendFile.sh $i
    done
    sleep 1
done