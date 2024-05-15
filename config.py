config = {
    "SOUNDS_PATH": 'sounds/',
    "WAKE_WORD": ["rasp", "berry", "barry", "razbear", "brad", "raster"],
    "TIMEOUT": 2,
    "PHRASE_TIME_LIMIT": 5,
    "WHISPER_CPP_PATH": "../whisper.cpp/",
    "WHISPER_MODEL_PATH": "/home/nkasmanoff/Desktop/whisper.cpp/models/ggml-tiny.en.bin",
    "LLAMA_CPP_PATH": "../md-gguf/llama.cpp/",
    "MOONDREAM_MMPROJ_PATH": "../moondream-quants/moondream2-mmproj-050824-f16.gguf",
    "MOONDREAM_MODEL_PATH": "../moondream-quants/moondream2-050824-q8.gguf",
    "VISION_MODEL": "moondream",
    "LOCAL_MODEL": "llama3:instruct",
    "STORE_CONVERSATIONS": True,
    "CONDENSE_MESSAGES": True,
    "SYSTEM_PROMPT": 'You are PiCard, a Raspbery Pi Voice Assistant. Please help users with brief answers.'
}
