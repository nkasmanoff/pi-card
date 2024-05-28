config = {
    "SOUNDS_PATH": 'sounds/',
    "WAKE_WORD": ["johnny", "five"],
    "TIMEOUT": 10,
    # longest amount of time the allow a phrase to continue before stopping the recording
    "PHRASE_TIME_LIMIT": 7,
    "USE_FASTER_WHISPER": False,
    "WHISPER_CPP_PATH": "/app/whisper.cpp/",
    "WHISPER_MODEL_PATH": "/app/whisper.cpp/models/ggml-tiny.en.bin",
    "LOCAL_MODEL": "phi3:instruct",  # better responses, higher latency
    "STORE_CONVERSATIONS": True,  # to save in case we you want to analyze later
    "CONDENSE_MESSAGES": True,  # for faster response time
    # number of messages to keep in memory (odd #s work best)
    "TRAILING_MESSAGE_COUNT": 1,
    "SYSTEM_PROMPT": 'You are Johnny5, a Raspbery Pi Voice Assistant. Answer questions in only a sentence.',
    "VISION_MODEL": None,
    "MICROPHONE_DEVICE_INDEX": 2,
}
