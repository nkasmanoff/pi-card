#!/bin/bash
aplay -l
arecord -l
ollama serve &
python main.py