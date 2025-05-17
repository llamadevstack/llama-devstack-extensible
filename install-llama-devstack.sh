#!/bin/bash
set -e

echo "Cloning llama-devstack..."
git clone https://github.com/llamadevstack/llama-devstack.git llama-devstack
cd llama-devstack

echo "Running setup..."
bash setup.sh

echo "Downloading models..."
cd python-llama-server
python download_models.py

echo "Launching services..."
cd ..
python launch_all.py