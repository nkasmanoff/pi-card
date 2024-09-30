config = {
    "SOUNDS_PATH": "/home/nkasmanoff/Desktop/pi-card/sounds/",
    "WAKE_WORD": ["rasp", "berry", "barry", "razbear", "brad", "raster"],
    "TIMEOUT": 10,
    # longest amount of time the allow a phrase to continue before stopping the recording
    "PHRASE_TIME_LIMIT": 7,
    "USE_FASTER_WHISPER": False,
    "WHISPER_CPP_PATH": "../whisper.cpp/",
    "WHISPER_MODEL_PATH": "/home/nkasmanoff/Desktop/whisper.cpp/models/ggml-tiny.en.bin",
    "LLAMA_CPP_PATH": "../md-gguf/llama.cpp/",
    "MOONDREAM_MMPROJ_PATH": "../moondream-quants/moondream2-mmproj-050824-f16.gguf",
    "MOONDREAM_MODEL_PATH": "../moondream-quants/moondream2-050824-q8.gguf",
    "VISION_MODEL": "none",
    "LOCAL_MODEL": "llama3.2:1b-instruct-q8_0",
    "RAG_MODEL": "gemma2:2b-instruct-q4_0",
    "STORE_CONVERSATIONS": True,  # to save in case we you want to analyze later
    "CONDENSE_MESSAGES": True,  # for faster response time
    # number of messages to keep in memory (odd #s work best)
    "TRAILING_MESSAGE_COUNT": 3,
    "SYSTEM_PROMPT": "You are Pi-Card, the Raspberry Pi AI assistant.",
}
