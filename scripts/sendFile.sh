#!/bin/bash

nodenum=$1

# Generate 64 random characters and save to a file
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64 > node-test/node$nodenum/input/random_file.txt

echo "File with 64 random characters created: random_file.txt"