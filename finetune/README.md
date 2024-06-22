# Finetune

This directory contains some experimental code for fine-tuning an LLM on Pi-Card data and other conversational data.

As smaller LLMs (< 3B params) can run quickly on a Raspberry Pi and grow more capabable, there is some potential for fine-tuning on outputs from previous conversations to improve performance.

Please note this notebook should not be run on the Pi itself! It depends on how much of the model you want to tune, but I would suggest at least 16GB of RAM.

The notebook demonstrates how to load chat data from Pi-Card and HuggingFace, fine-tune the model, then convert it to .gguf format and then ollama format, so that it could be run on the Raspberry Pi. similar to the original versions.
