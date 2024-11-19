#!/bin/bash
set -e


ollama serve &
# download model
#ollama pull gemma2:2b-instruct-q4_0
# Check if running in button mode
if [ "$USE_BUTTON" = "true" ]; then
    echo "Starting in button mode..."
    exec python main_button.py
else
    echo "Starting in wake word mode..."
    exec python main.py
fi