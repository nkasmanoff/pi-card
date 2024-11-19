#!/bin/bash
aplay -l
arecord -l
espeak "Hello. Docker is ready."
espeak "Testing espeak."
ollama serve &
python main.py