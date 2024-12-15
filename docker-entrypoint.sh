#!/bin/bash
set -e


ollama serve &
# download model if not already downloaded (this is done in docker-compose.yml)
ollama pull $OLLAMA_MODEL

# Check if running in button mode
if [ "$USE_BUTTON" = "true" ]; then
    echo "Starting in button mode..."
    exec python main_button.py
else
    echo "Starting in wake word mode..."
    exec python main.py
fi