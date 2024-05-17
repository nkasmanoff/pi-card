config = {
    "SOUNDS_PATH": 'sounds/',
    "WAKE_WORD": ["rasp", "berry", "barry", "razbear", "brad", "raster"],
    "TIMEOUT": 5,
    "PHRASE_TIME_LIMIT": 5,
    "WHISPER_CPP_PATH": "../whisper.cpp/",
    "WHISPER_MODEL_PATH": "/home/nkasmanoff/Desktop/whisper.cpp/models/ggml-base.en.bin",
    "LLAMA_CPP_PATH": "../md-gguf/llama.cpp/",
    "MOONDREAM_MMPROJ_PATH": "../moondream-quants/moondream2-mmproj-050824-f16.gguf",
    "MOONDREAM_MODEL_PATH": "../moondream-quants/moondream2-050824-q8.gguf",
    "VISION_MODEL": "moondream",
    "LOCAL_MODEL": "llama3:instruct",  # better responses, higher latency
    "STORE_CONVERSATIONS": True,  # to save in case we you want to analyze later
    "CONDENSE_MESSAGES": True,  # for faster response time
    "SYSTEM_PROMPT": 'You are PiCard, a witty Raspbery Pi Voice Assistant. Please help by answering questions in only a sentence or two.'
}
